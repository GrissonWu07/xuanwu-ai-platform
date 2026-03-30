import tempfile
import unittest
import sys
import types
import asyncio
import os
from pathlib import Path
from unittest.mock import patch

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
    load_bootstrap_config,
    load_config,
    merge_configs,
    ensure_directories,
    read_config,
    should_use_dynamic_server_config,
    should_use_private_config_resolution,
)
import config.config_loader as config_loader_module
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
        engine = TemplateFallbackDialogueEngine("XuanWu is unavailable right now.")

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
        self.assertEqual("XuanWu is unavailable right now.", conn.tts.calls[0][1])
        self.assertEqual(1, len(conn.dialogue.messages))
        self.assertEqual(
            "XuanWu is unavailable right now.",
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

    def test_load_bootstrap_config_merges_default_custom_and_environment_overrides(self):
        project_root = self.root / "project"
        (project_root / "data").mkdir(parents=True, exist_ok=True)
        (project_root / "config.yaml").write_text(
            yaml.safe_dump(
                {
                    "server": {"ip": "0.0.0.0", "port": 8000},
                    "prompt_template": "default-prompt.txt",
                    "xuanwu-management-server": {
                        "enabled": False,
                        "url": "http://127.0.0.1:18082",
                        "secret": "bootstrap-secret",
                    },
                },
                allow_unicode=True,
            ),
            encoding="utf-8",
        )
        (project_root / "data" / ".config.yaml").write_text(
            yaml.safe_dump(
                {
                    "server": {"port": 18080},
                    "prompt_template": "custom-prompt.txt",
                },
                allow_unicode=True,
            ),
            encoding="utf-8",
        )
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
        os.environ["XUANWU_MANAGEMENT_SERVER_URL"] = "http://mgmt.cluster.local:18082"
        os.environ["XUANWU_MANAGEMENT_SERVER_SECRET"] = "env-secret"
        os.environ["XUANWU_MANAGEMENT_SERVER_ENABLED"] = "true"

        try:
            with patch.object(
                config_loader_module,
                "get_project_dir",
                return_value=str(project_root) + os.sep,
            ):
                config = load_bootstrap_config()
        finally:
            for key, value in previous.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

        self.assertEqual(18080, config["server"]["port"])
        self.assertEqual("0.0.0.0", config["server"]["ip"])
        self.assertEqual("custom-prompt.txt", config["prompt_template"])
        self.assertEqual(
            "http://mgmt.cluster.local:18082",
            config["xuanwu-management-server"]["url"],
        )
        self.assertEqual("env-secret", config["xuanwu-management-server"]["secret"])
        self.assertTrue(config["xuanwu-management-server"]["enabled"])

    def test_load_config_fetches_once_and_reuses_cached_runtime_config(self):
        cache_module = types.ModuleType("core.utils.cache.manager")

        class DummyCacheType:
            CONFIG = "config"

        class DummyCacheManager:
            def __init__(self):
                self.values = {}

            def get(self, cache_type, key):
                return self.values.get((cache_type, key))

            def set(self, cache_type, key, value):
                self.values[(cache_type, key)] = value

        cache_module.CacheType = DummyCacheType
        cache_module.cache_manager = DummyCacheManager()
        sys.modules["core.utils.cache.manager"] = cache_module

        bootstrap_config = {
            "server": {"ip": "127.0.0.1", "port": 8000},
            "selected_module": {"LLM": "OpenAI"},
            "xuanwu-management-server": {
                "enabled": True,
                "url": "http://management.internal:18082",
                "secret": "runtime-secret",
            },
        }
        resolved_runtime = {
            "server": {"runtime_secret": "runtime-secret", "auth": {"enabled": True}},
            "selected_module": {"LLM": "OpenAI"},
            "prompt_template": "ops-floor-assistant.txt",
        }
        fetch_calls = []

        async def fake_dynamic_resolution(config):
            fetch_calls.append(config["xuanwu-management-server"]["url"])
            return resolved_runtime

        with patch.object(
            config_loader_module,
            "load_bootstrap_config",
            return_value=bootstrap_config,
        ), patch.object(
            config_loader_module,
            "get_config_from_api_async",
            side_effect=fake_dynamic_resolution,
        ), patch.object(
            config_loader_module,
            "ensure_directories",
        ) as ensure_dirs:
            first = load_config()
            second = load_config()

        self.assertEqual(resolved_runtime, first)
        self.assertEqual(resolved_runtime, second)
        self.assertEqual(["http://management.internal:18082"], fetch_calls)
        ensure_dirs.assert_called_once_with(resolved_runtime)

    def test_ensure_directories_creates_runtime_output_paths(self):
        project_root = self.root / "runtime-project"
        project_root.mkdir(parents=True, exist_ok=True)
        config = {
            "log": {"log_dir": "logs/runtime"},
            "ASR": {
                "aliyun": {
                    "output_dir": str(project_root / "artifacts" / "asr"),
                }
            },
            "TTS": {
                "edge": {
                    "output_dir": str(project_root / "artifacts" / "tts"),
                }
            },
            "selected_module": {"ASR": "aliyun", "TTS": "edge"},
        }

        with patch.object(
            config_loader_module,
            "get_project_dir",
            return_value=str(project_root) + os.sep,
        ):
            ensure_directories(config)

        self.assertTrue((project_root / "logs" / "runtime").is_dir())
        self.assertTrue((project_root / "artifacts" / "asr").is_dir())
        self.assertTrue((project_root / "artifacts" / "tts").is_dir())

    def test_merge_configs_recursively_preserves_nested_defaults(self):
        default = {
            "server": {"ip": "0.0.0.0", "port": 8000, "auth": {"enabled": True}},
            "selected_module": {"LLM": "BaseLLM"},
        }
        custom = {
            "server": {"port": 18080, "auth": {"enabled": False}},
            "selected_module": {"TTS": "EdgeTTS"},
        }

        merged = merge_configs(default, custom)

        self.assertEqual(
            {
                "server": {"ip": "0.0.0.0", "port": 18080, "auth": {"enabled": False}},
                "selected_module": {"LLM": "BaseLLM", "TTS": "EdgeTTS"},
            },
            merged,
        )

if __name__ == "__main__":
    unittest.main()
