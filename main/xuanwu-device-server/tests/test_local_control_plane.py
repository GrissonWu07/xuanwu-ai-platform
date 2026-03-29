import tempfile
import unittest
import sys
import types
import asyncio
import os
from pathlib import Path

import yaml
from aiohttp import web
from aiohttp.test_utils import make_mocked_request

SERVICE_ROOT = Path(__file__).resolve().parents[1]
if str(SERVICE_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVICE_ROOT))
for module_name in list(sys.modules):
    if module_name == "config" or module_name.startswith("config."):
        sys.modules.pop(module_name, None)
    if module_name == "core" or module_name.startswith("core."):
        sys.modules.pop(module_name, None)

from config.config_loader import (
    apply_environment_overrides,
    get_config_from_api_async,
    get_private_config_from_api,
    read_config,
    should_use_dynamic_server_config,
    should_use_private_config_resolution,
)
from config.config_loader import resolve_control_secret
from config.xuanwu_management_client import is_xuanwu_management_server_enabled
from core.providers.agent.template_fallback import TemplateFallbackDialogueEngine


class _DummyLogger:
    def bind(self, **kwargs):
        return self

    def info(self, *args, **kwargs):
        return None

    def warning(self, *args, **kwargs):
        return None

    def error(self, *args, **kwargs):
        return None

    def debug(self, *args, **kwargs):
        return None


fake_logger_module = types.ModuleType("config.logger")
fake_logger_module.setup_logging = lambda: _DummyLogger()
sys.modules.setdefault("config.logger", fake_logger_module)

class XuanwuManagementConfigTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        (self.root / "agents").mkdir(parents=True, exist_ok=True)
        (self.root / "devices").mkdir(parents=True, exist_ok=True)

        self.base_config = {
            "prompt": "base prompt",
            "prompt_template": "agent-base-prompt.txt",
            "selected_module": {
                "LLM": "BaseLLM",
                "TTS": "BaseTTS",
                "VLLM": "BaseVision",
            },
            "LLM": {"BaseLLM": {"type": "openai", "model_name": "base-llm"}},
            "TTS": {"BaseTTS": {"type": "edge"}},
            "VLLM": {"BaseVision": {"type": "vision"}},
            "plugins": {"get_weather": {"enabled": True}},
            "context_providers": [],
        }

    def tearDown(self):
        self.temp_dir.cleanup()

    def _write_yaml(self, relative_path: str, payload: dict):
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")

    def test_read_config_returns_empty_mapping_for_empty_file(self):
        config_path = self.root / "empty-config.yaml"
        config_path.write_text("", encoding="utf-8")

        self.assertEqual({}, read_config(str(config_path)))

    def test_dynamic_server_config_only_depends_on_xuanwu_management_server(self):
        self.assertFalse(
            should_use_dynamic_server_config(
                {
                    "control-plane": {"enabled": True, "data_dir": str(self.root)},
                    "xuanwu-management-server": {"enabled": False, "url": ""},
                    "manager-api": {"enabled": True, "url": "http://legacy-manager"},
                }
            )
        )
        self.assertTrue(
            should_use_dynamic_server_config(
                {
                    "xuanwu-management-server": {
                        "enabled": True,
                        "url": "http://127.0.0.1:18082",
                    }
                }
            )
        )

    def test_private_config_resolution_only_depends_on_xuanwu_management_server(self):
        self.assertFalse(
            should_use_private_config_resolution(
                {
                    "control-plane": {"enabled": True, "data_dir": str(self.root)},
                    "xuanwu-management-server": {"enabled": False, "url": ""},
                    "manager-api": {"enabled": True, "url": "http://legacy-manager"},
                }
            )
        )
        self.assertTrue(
            should_use_private_config_resolution(
                {
                    "xuanwu-management-server": {
                        "enabled": True,
                        "url": "http://127.0.0.1:18082",
                    }
                }
            )
        )

    def test_get_config_from_api_async_uses_xuanwu_management_server_even_when_legacy_sources_exist(self):
        async def scenario():
            received: dict[str, str] = {}

            async def handle_server_config(request: web.Request):
                received["path"] = request.path
                received["secret"] = request.headers.get("X-Xuanwu-Control-Secret", "")
                return web.json_response(
                    {
                        "server": {"runtime_secret": "mgmt-runtime-secret"},
                        "prompt": "management prompt",
                    }
                )

            upstream = web.Application()
            upstream.router.add_get(
                "/control-plane/v1/config/server",
                handle_server_config,
            )
            runner = web.AppRunner(upstream)
            await runner.setup()
            site = web.TCPSite(runner, "127.0.0.1", 0)
            await site.start()
            sockets = site._server.sockets
            self.assertTrue(sockets)
            port = sockets[0].getsockname()[1]

            config = {
                **self.base_config,
                "control-plane": {"enabled": True, "data_dir": str(self.root)},
                "manager-api": {
                    "enabled": True,
                    "url": "http://legacy-manager.internal",
                    "secret": "legacy-secret",
                },
                "xuanwu-management-server": {
                    "enabled": True,
                    "url": f"http://127.0.0.1:{port}",
                    "secret": "mgmt-secret-001",
                },
            }
            resolved = await get_config_from_api_async(config)

            await runner.cleanup()

            self.assertEqual("management prompt", resolved["prompt"])
            self.assertEqual(
                "mgmt-runtime-secret",
                resolved["server"]["runtime_secret"],
            )
            self.assertTrue(resolved["read_config_from_api"])
            self.assertEqual(
                {
                    "path": "/control-plane/v1/config/server",
                    "secret": "mgmt-secret-001",
                },
                received,
            )

        asyncio.run(scenario())

    def test_get_private_config_from_api_uses_xuanwu_management_server_even_when_legacy_sources_exist(self):
        async def scenario():
            received: dict[str, object] = {}

            async def handle_resolve(request: web.Request):
                received["path"] = request.path
                received["secret"] = request.headers.get("X-Xuanwu-Control-Secret", "")
                received["payload"] = await request.json()
                return web.json_response(
                    {
                        "resolved_config": {
                            "prompt": "remote agent prompt",
                            "selected_module": {"LLM": "RemoteLLM"},
                        }
                    }
                )

            upstream = web.Application()
            upstream.router.add_post(
                "/control-plane/v1/runtime/device-config:resolve",
                handle_resolve,
            )
            runner = web.AppRunner(upstream)
            await runner.setup()
            site = web.TCPSite(runner, "127.0.0.1", 0)
            await site.start()
            sockets = site._server.sockets
            self.assertTrue(sockets)
            port = sockets[0].getsockname()[1]

            config = {
                **self.base_config,
                "control-plane": {"enabled": True, "data_dir": str(self.root)},
                "manager-api": {
                    "enabled": True,
                    "url": "http://legacy-manager.internal",
                    "secret": "legacy-secret",
                },
                "xuanwu-management-server": {
                    "enabled": True,
                    "url": f"http://127.0.0.1:{port}",
                    "secret": "mgmt-secret-002",
                },
            }

            resolved = await get_private_config_from_api(
                config,
                "esp32-remote-001",
                "client-remote-001",
            )

            await runner.cleanup()

            self.assertEqual("remote agent prompt", resolved["prompt"])
            self.assertEqual("RemoteLLM", resolved["selected_module"]["LLM"])
            self.assertEqual(
                {
                    "path": "/control-plane/v1/runtime/device-config:resolve",
                    "secret": "mgmt-secret-002",
                    "payload": {
                        "device_id": "esp32-remote-001",
                        "client_id": "client-remote-001",
                        "selected_module": self.base_config["selected_module"],
                    },
                },
                received,
            )

        asyncio.run(scenario())

    def test_template_fallback_speaks_and_records_reply(self):
        engine = TemplateFallbackDialogueEngine("AtlasClaw is unavailable right now.")

        class DummyTTS:
            def __init__(self):
                self.calls = []

            def tts_one_sentence(self, conn, content_type, content_detail):
                self.calls.append((content_type, content_detail))

        class DummyDialogue:
            def __init__(self):
                self.messages = []

            def put(self, message):
                self.messages.append(message)

        class DummyConn:
            def __init__(self):
                self.tts = DummyTTS()
                self.dialogue = DummyDialogue()

        conn = DummyConn()

        __import__("asyncio").run(engine.run_turn(conn, "hello"))

        self.assertEqual(1, len(conn.tts.calls))
        self.assertEqual("AtlasClaw is unavailable right now.", conn.tts.calls[0][1])
        self.assertEqual(1, len(conn.dialogue.messages))
        self.assertEqual(
            "AtlasClaw is unavailable right now.",
            conn.dialogue.messages[0].content,
        )

    def test_control_secret_prefers_control_plane_secret_over_auth_key(self):
        config = {
            "server": {"auth_key": "server-auth"},
            "control-plane": {"secret": "control-secret"},
            "manager-api": {"secret": "manager-secret"},
        }

        self.assertEqual("control-secret", resolve_control_secret(config))

    def test_control_secret_ignores_disabled_manager_api_secret(self):
        config = {
            "server": {},
            "control-plane": {},
            "manager-api": {
                "enabled": False,
                "url": "http://legacy-manager.internal",
                "secret": "manager-secret",
            },
        }

        self.assertEqual("", resolve_control_secret(config))

    def test_control_secret_never_uses_manager_api_secret_even_when_enabled(self):
        config = {
            "server": {},
            "control-plane": {},
            "manager-api": {
                "enabled": True,
                "url": "http://legacy-manager.internal",
                "secret": "legacy-manager-secret",
            },
        }

        self.assertEqual("", resolve_control_secret(config))

    def test_xuanwu_management_server_respects_enabled_flag(self):
        self.assertFalse(
            is_xuanwu_management_server_enabled(
                {
                    "xuanwu-management-server": {
                        "enabled": False,
                        "url": "http://127.0.0.1:18082",
                    }
                }
            )
        )

    def test_environment_overrides_can_enable_xuanwu_management_server(self):
        config = {
            "xuanwu-management-server": {
                "enabled": False,
                "url": "http://127.0.0.1:18082",
                "secret": "local-secret",
            }
        }

        previous = {
            "XUANWU_MANAGEMENT_SERVER_URL": os.environ.get(
                "XUANWU_MANAGEMENT_SERVER_URL"
            ),
            "XUANWU_MANAGEMENT_SERVER_SECRET": os.environ.get(
                "XUANWU_MANAGEMENT_SERVER_SECRET"
            ),
            "XUANWU_MANAGEMENT_SERVER_ENABLED": os.environ.get(
                "XUANWU_MANAGEMENT_SERVER_ENABLED"
            ),
        }
        os.environ["XUANWU_MANAGEMENT_SERVER_URL"] = "http://mgmt.internal:18082"
        os.environ["XUANWU_MANAGEMENT_SERVER_SECRET"] = "env-secret"
        os.environ["XUANWU_MANAGEMENT_SERVER_ENABLED"] = "true"

        try:
            overridden = apply_environment_overrides(config)
        finally:
            for key, value in previous.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

        self.assertTrue(overridden["xuanwu-management-server"]["enabled"])
        self.assertEqual(
            "http://mgmt.internal:18082",
            overridden["xuanwu-management-server"]["url"],
        )
        self.assertEqual(
            "env-secret",
            overridden["xuanwu-management-server"]["secret"],
        )
        self.assertTrue(
            is_xuanwu_management_server_enabled(
                {
                    "xuanwu-management-server": {
                        "enabled": True,
                        "url": "http://127.0.0.1:18082",
                    }
                }
            )
        )

if __name__ == "__main__":
    unittest.main()
