import tempfile
import unittest
import sys
import types
from pathlib import Path

import yaml
from aiohttp.test_utils import make_mocked_request

from config.config_loader import get_config_from_api_async, get_private_config_from_api
from config.config_loader import is_manager_api_enabled, resolve_control_secret
from core.control_plane.import_bundle import import_control_plane_bundle
from core.control_plane.local_store import LocalControlPlaneStore
from core.control_plane.exceptions import DeviceBindException, DeviceNotFoundException
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

from core.api.control_plane_handler import ControlPlaneHandler


class LocalControlPlaneStoreTests(unittest.TestCase):
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

    def test_resolve_device_config_merges_agent_and_device_overrides(self):
        self._write_yaml(
            "server.yaml",
            {
                "server": {"runtime_secret": "runtime-secret"},
            },
        )
        self._write_yaml(
            "agents/default.yaml",
            {
                "agent_id": "default",
                "prompt": "agent prompt",
                "selected_module": {"LLM": "AgentLLM", "VLLM": "AgentVision"},
                "LLM": {"AgentLLM": {"type": "openai", "model_name": "agent-llm"}},
                "VLLM": {"AgentVision": {"type": "vision", "model_name": "agent-vllm"}},
            },
        )
        self._write_yaml(
            "devices/esp32-001.yaml",
            {
                "device_id": "esp32-001",
                "agent_id": "default",
                "bind_status": "bound",
                "runtime_overrides": {
                    "prompt": "device prompt",
                    "selected_module": {"TTS": "DeviceTTS"},
                    "TTS": {"DeviceTTS": {"type": "edge", "voice": "xiaozhi"}},
                },
            },
        )

        store = LocalControlPlaneStore(self.root)
        resolved = store.resolve_device_config(
            self.base_config,
            device_id="esp32-001",
            client_id="client-a",
            selected_module={"VLLM": "RequestVision"},
        )

        self.assertEqual("bound", resolved["device"]["bind_status"])
        self.assertEqual("default", resolved["agent"]["agent_id"])
        self.assertEqual("device prompt", resolved["resolved_config"]["prompt"])
        self.assertEqual(
            {
                "LLM": "AgentLLM",
                "TTS": "DeviceTTS",
                "VLLM": "RequestVision",
            },
            {
                key: resolved["resolved_config"]["selected_module"][key]
                for key in ("LLM", "TTS", "VLLM")
            },
        )
        self.assertEqual(
            "runtime-secret",
            resolved["resolved_config"]["server"]["runtime_secret"],
        )

    def test_resolve_device_config_raises_bind_exception_for_pending_device(self):
        self._write_yaml(
            "devices/esp32-002.yaml",
            {
                "device_id": "esp32-002",
                "agent_id": "default",
                "bind_status": "pending",
                "bind_code": "123456",
            },
        )

        store = LocalControlPlaneStore(self.root)

        with self.assertRaises(DeviceBindException) as ctx:
            store.resolve_device_config(self.base_config, "esp32-002", "client-b")

        self.assertEqual("123456", ctx.exception.bind_code)

    def test_resolve_device_config_raises_not_found_for_unknown_device(self):
        store = LocalControlPlaneStore(self.root)

        with self.assertRaises(DeviceNotFoundException):
            store.resolve_device_config(self.base_config, "missing-device", "client-c")

    def test_get_config_from_api_async_prefers_local_control_plane(self):
        self._write_yaml(
            "server.yaml",
            {
                "server": {"runtime_secret": "runtime-secret"},
                "prompt": "control-plane prompt",
            },
        )
        bootstrap_config = {
            **self.base_config,
            "control-plane": {
                "enabled": True,
                "data_dir": str(self.root),
            },
            "manager-api": {},
        }

        resolved = __import__("asyncio").run(get_config_from_api_async(bootstrap_config))

        self.assertEqual("runtime-secret", resolved["server"]["runtime_secret"])
        self.assertEqual("control-plane prompt", resolved["prompt"])
        self.assertFalse(resolved.get("read_config_from_api", False))

    def test_get_private_config_from_api_prefers_local_control_plane(self):
        self._write_yaml(
            "agents/default.yaml",
            {
                "agent_id": "default",
                "prompt": "agent prompt",
                "selected_module": {"LLM": "AgentLLM"},
                "LLM": {"AgentLLM": {"type": "openai", "model_name": "agent-llm"}},
            },
        )
        self._write_yaml(
            "devices/esp32-003.yaml",
            {
                "device_id": "esp32-003",
                "agent_id": "default",
                "bind_status": "bound",
            },
        )
        bootstrap_config = {
            **self.base_config,
            "control-plane": {
                "enabled": True,
                "data_dir": str(self.root),
            },
            "manager-api": {},
        }

        resolved = __import__("asyncio").run(
            get_private_config_from_api(bootstrap_config, "esp32-003", "client-z")
        )

        self.assertEqual("agent prompt", resolved["prompt"])
        self.assertEqual("AgentLLM", resolved["selected_module"]["LLM"])

    def test_control_plane_get_server_config_requires_secret_and_returns_payload(self):
        self._write_yaml(
            "server.yaml",
            {
                "server": {"runtime_secret": "runtime-secret"},
                "prompt": "control-plane prompt",
            },
        )
        config = {
            **self.base_config,
            "server": {"auth_key": "runtime-secret"},
            "control-plane": {
                "enabled": True,
                "data_dir": str(self.root),
            },
        }
        handler = ControlPlaneHandler(config)
        request = make_mocked_request(
            "GET",
            "/control-plane/v1/config/server",
            headers={"X-Xiaozhi-Control-Secret": "runtime-secret"},
        )

        response = __import__("asyncio").run(handler.handle_get_server_config(request))

        self.assertEqual(200, response.status)
        payload = yaml.safe_load(response.text)
        self.assertEqual("control-plane prompt", payload["prompt"])

    def test_control_plane_runtime_resolve_returns_device_and_agent_snapshot(self):
        self._write_yaml(
            "agents/default.yaml",
            {
                "agent_id": "default",
                "prompt": "agent prompt",
                "selected_module": {"LLM": "AgentLLM"},
                "LLM": {"AgentLLM": {"type": "openai", "model_name": "agent-llm"}},
            },
        )
        self._write_yaml(
            "devices/esp32-004.yaml",
            {
                "device_id": "esp32-004",
                "agent_id": "default",
                "bind_status": "bound",
            },
        )
        config = {
            **self.base_config,
            "server": {"auth_key": "runtime-secret"},
            "control-plane": {
                "enabled": True,
                "data_dir": str(self.root),
            },
        }
        handler = ControlPlaneHandler(config)
        request = make_mocked_request(
            "POST",
            "/control-plane/v1/runtime/device-config:resolve",
            headers={"X-Xiaozhi-Control-Secret": "runtime-secret"},
        )
        request._read_bytes = b'{"device_id":"esp32-004","client_id":"client-r","selected_module":{"TTS":"EdgeTTS"}}'

        response = __import__("asyncio").run(handler.handle_resolve_device_config(request))

        self.assertEqual(200, response.status)
        payload = yaml.safe_load(response.text)
        self.assertEqual("bound", payload["device"]["bind_status"])
        self.assertEqual("default", payload["agent"]["agent_id"])
        self.assertEqual("EdgeTTS", payload["agent"]["modules"]["TTS"])

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

    def test_manager_api_helper_only_depends_on_url(self):
        self.assertTrue(is_manager_api_enabled({"manager-api": {"url": "http://example"}}))
        self.assertFalse(is_manager_api_enabled({"manager-api": {}}))

    def test_import_control_plane_bundle_writes_server_agents_and_devices(self):
        store = LocalControlPlaneStore(self.root)
        summary = import_control_plane_bundle(
            store,
            {
                "server": {"server": {"runtime_secret": "secret-a"}},
                "agents": [
                    {
                        "agent_id": "default",
                        "prompt": "agent prompt",
                    }
                ],
                "devices": {
                    "esp32-005": {
                        "bind_status": "bound",
                        "agent_id": "default",
                    }
                },
            },
        )

        self.assertEqual({"server": 1, "agents": 1, "devices": 1}, summary)
        self.assertEqual("secret-a", store.load_server_profile()["server"]["runtime_secret"])
        self.assertEqual("agent prompt", store.get_agent("default")["prompt"])
        self.assertEqual("bound", store.get_device("esp32-005")["bind_status"])


if __name__ == "__main__":
    unittest.main()
