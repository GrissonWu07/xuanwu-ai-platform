import asyncio
import tempfile
from pathlib import Path

import yaml
from aiohttp.test_utils import make_mocked_request


SERVICE_ROOT = Path(__file__).resolve().parents[1]
import sys

if str(SERVICE_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVICE_ROOT))
for module_name in list(sys.modules):
    if module_name == "config" or module_name.startswith("config."):
        sys.modules.pop(module_name, None)
    if module_name == "core" or module_name.startswith("core."):
        sys.modules.pop(module_name, None)

from core.api.control_plane_handler import ControlPlaneHandler
from core.store.exceptions import DeviceBindException
from core.store.import_bundle import import_control_plane_bundle
from core.store.local_store import LocalControlPlaneStore


def _write_yaml(root: Path, relative_path: str, payload: dict):
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")


def test_resolve_device_config_merges_agent_and_device_overrides():
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        _write_yaml(
            root,
            "server.yaml",
            {"server": {"runtime_secret": "runtime-secret"}},
        )
        _write_yaml(
            root,
            "agents/default.yaml",
            {
                "agent_id": "default",
                "prompt": "agent prompt",
                "selected_module": {"LLM": "AgentLLM"},
            },
        )
        _write_yaml(
            root,
            "devices/esp32-living-room.yaml",
            {
                "device_id": "esp32-living-room",
                "agent_id": "default",
                "bind_status": "bound",
                "runtime_overrides": {
                    "prompt": "device prompt",
                    "selected_module": {"TTS": "EdgeTTS"},
                },
            },
        )
        store = LocalControlPlaneStore(root)

        resolved = store.resolve_device_config(
            {
                "prompt": "base prompt",
                "selected_module": {"VLLM": "BaseVision"},
            },
            device_id="esp32-living-room",
            client_id="client-001",
            selected_module={"VLLM": "RequestedVision"},
        )

        assert resolved["device"]["bind_status"] == "bound"
        assert resolved["agent"]["agent_id"] == "default"
        assert resolved["resolved_config"]["prompt"] == "device prompt"
        assert resolved["resolved_config"]["selected_module"] == {
            "LLM": "AgentLLM",
            "TTS": "EdgeTTS",
            "VLLM": "RequestedVision",
        }


def test_resolve_device_config_prefers_active_device_agent_mapping():
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        _write_yaml(
            root,
            "server.yaml",
            {"server": {"runtime_secret": "runtime-secret"}},
        )
        _write_yaml(
            root,
            "agents/agent-frontdesk.yaml",
            {
                "agent_id": "agent-frontdesk",
                "prompt": "mapped agent prompt",
                "selected_module": {"LLM": "MappedLLM"},
            },
        )
        _write_yaml(
            root,
            "devices/esp32-frontdesk.yaml",
            {
                "device_id": "esp32-frontdesk",
                "bind_status": "bound",
                "runtime_overrides": {"selected_module": {"TTS": "DeskTTS"}},
            },
        )
        _write_yaml(
            root,
            "device_agent_mappings/map-device-agent-001.yaml",
            {
                "mapping_id": "map-device-agent-001",
                "device_id": "esp32-frontdesk",
                "agent_id": "agent-frontdesk",
                "enabled": True,
            },
        )
        store = LocalControlPlaneStore(root)

        resolved = store.resolve_device_config({}, "esp32-frontdesk", "client-frontdesk")

        assert resolved["device"]["agent_id"] == "agent-frontdesk"
        assert resolved["binding"]["mapping_id"] == "map-device-agent-001"
        assert resolved["agent"]["agent_id"] == "agent-frontdesk"
        assert resolved["resolved_config"]["selected_module"] == {
            "LLM": "MappedLLM",
            "TTS": "DeskTTS",
        }


def test_resolve_device_config_raises_bind_exception_for_pending_device():
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        _write_yaml(
            root,
            "devices/esp32-study.yaml",
            {
                "device_id": "esp32-study",
                "agent_id": "default",
                "bind_status": "pending",
                "bind_code": "654321",
            },
        )
        store = LocalControlPlaneStore(root)

        try:
            store.resolve_device_config({}, "esp32-study", "client-002")
        except DeviceBindException as exc:
            assert exc.bind_code == "654321"
        else:
            raise AssertionError("Expected DeviceBindException")


def test_control_plane_get_server_config_requires_secret_and_returns_payload():
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        _write_yaml(
            root,
            "server.yaml",
            {
                "server": {"runtime_secret": "runtime-secret"},
                "prompt": "control-plane prompt",
            },
        )
        handler = ControlPlaneHandler(
            {
                "server": {"auth_key": "runtime-secret"},
                "control-plane": {"data_dir": str(root)},
            }
        )
        request = make_mocked_request(
            "GET",
            "/control-plane/v1/config/server",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
        )

        response = asyncio.run(handler.handle_get_server_config(request))
        payload = yaml.safe_load(response.text)

        assert response.status == 200
        assert payload["prompt"] == "control-plane prompt"


def test_import_control_plane_bundle_writes_server_agents_and_devices():
    with tempfile.TemporaryDirectory() as temp_dir:
        store = LocalControlPlaneStore(Path(temp_dir))

        summary = import_control_plane_bundle(
            store,
            {
                "server": {"server": {"runtime_secret": "secret-a"}},
                "agents": [
                    {"agent_id": "default", "prompt": "agent prompt"},
                ],
                "devices": {
                    "esp32-kitchen": {
                        "bind_status": "bound",
                        "agent_id": "default",
                    }
                },
            },
        )

        assert summary == {"server": 1, "agents": 1, "devices": 1}
        assert store.load_server_profile()["server"]["runtime_secret"] == "secret-a"
        assert store.get_agent("default")["prompt"] == "agent prompt"
        assert store.get_device("esp32-kitchen")["bind_status"] == "bound"


def test_control_plane_chat_history_report_persists_payload():
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        handler = ControlPlaneHandler(
            {
                "server": {"auth_key": "runtime-secret"},
                "control-plane": {"data_dir": str(root)},
            }
        )
        request = make_mocked_request(
            "POST",
            "/control-plane/v1/chat-history/report",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
        )
        request._read_bytes = (
            b'{"device_id":"esp32-living-room","session_id":"sess-20260328-001",'
            b'"chat_type":1,"content":"\xe4\xbb\x8a\xe5\xa4\xa9\xe6\x9d\xad\xe5\xb7\x9e\xe5\xa4\xa9\xe6\xb0\x94\xe6\x80\x8e\xe4\xb9\x88\xe6\xa0\xb7",'
            b'"report_time":1711612800,"audio_base64":"UklGRg=="}'
        )

        response = asyncio.run(handler.handle_report_chat_history(request))
        payload = yaml.safe_load(response.text)

        assert response.status == 201
        assert payload["session_id"] == "sess-20260328-001"
        records = handler.store.load_chat_history("sess-20260328-001")
        assert len(records) == 1
        assert records[0]["device_id"] == "esp32-living-room"
        assert records[0]["content"] == "今天杭州天气怎么样"


def test_control_plane_summary_generation_request_persists_payload():
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        handler = ControlPlaneHandler(
            {
                "server": {"auth_key": "runtime-secret"},
                "control-plane": {"data_dir": str(root)},
            }
        )
        request = make_mocked_request(
            "POST",
            "/control-plane/v1/chat-summaries/sess-20260328-001:generate",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
            match_info={"summary_id": "sess-20260328-001"},
        )
        request._read_bytes = (
            b'{"reason":"memory_rollup","requested_by":"xuanwu-device-server"}'
        )

        response = asyncio.run(handler.handle_generate_chat_summary(request))
        payload = yaml.safe_load(response.text)

        assert response.status == 202
        assert payload["summary_id"] == "sess-20260328-001"
        summary_request = handler.store.get_summary_request("sess-20260328-001")
        assert summary_request["reason"] == "memory_rollup"
        assert summary_request["requested_by"] == "xuanwu-device-server"


def test_control_plane_create_user_and_channel_persists_payloads():
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        handler = ControlPlaneHandler(
            {
                "server": {"auth_key": "runtime-secret"},
                "control-plane": {"data_dir": str(root)},
            }
        )
        user_request = make_mocked_request(
            "POST",
            "/control-plane/v1/users",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
        )
        user_request._read_bytes = b'{"user_id":"user-001","name":"Alice"}'

        channel_request = make_mocked_request(
            "POST",
            "/control-plane/v1/channels",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
        )
        channel_request._read_bytes = b'{"channel_id":"channel-home","user_id":"user-001","name":"Home"}'

        user_response = asyncio.run(handler.handle_create_user(user_request))
        channel_response = asyncio.run(handler.handle_create_channel(channel_request))

        assert user_response.status == 201
        assert channel_response.status == 201
        assert handler.store.get_user("user-001")["name"] == "Alice"
        assert handler.store.get_channel("channel-home")["user_id"] == "user-001"


def test_control_plane_rejects_user_and_channel_without_ids():
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        handler = ControlPlaneHandler(
            {
                "server": {"auth_key": "runtime-secret"},
                "control-plane": {"data_dir": str(root)},
            }
        )
        user_request = make_mocked_request(
            "POST",
            "/control-plane/v1/users",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
        )
        user_request._read_bytes = b'{"name":"Alice"}'

        channel_request = make_mocked_request(
            "POST",
            "/control-plane/v1/channels",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
        )
        channel_request._read_bytes = b'{"user_id":"user-001","name":"Home"}'

        user_response = asyncio.run(handler.handle_create_user(user_request))
        channel_response = asyncio.run(handler.handle_create_channel(channel_request))

        assert user_response.status == 400
        assert yaml.safe_load(user_response.text)["error"] == "user_id_required"
        assert channel_response.status == 400
        assert yaml.safe_load(channel_response.text)["error"] == "channel_id_required"


def test_control_plane_runtime_resolve_returns_binding_view():
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        _write_yaml(
            root,
            "agents/agent-frontdesk.yaml",
            {
                "agent_id": "agent-frontdesk",
                "prompt": "mapped agent prompt",
            },
        )
        _write_yaml(
            root,
            "devices/dev-001.yaml",
            {
                "device_id": "dev-001",
                "bind_status": "bound",
            },
        )
        _write_yaml(
            root,
            "device_agent_mappings/map-device-agent-001.yaml",
            {
                "mapping_id": "map-device-agent-001",
                "device_id": "dev-001",
                "agent_id": "agent-frontdesk",
                "enabled": True,
            },
        )
        handler = ControlPlaneHandler(
            {
                "server": {"auth_key": "runtime-secret"},
                "control-plane": {"data_dir": str(root)},
            }
        )
        request = make_mocked_request(
            "POST",
            "/control-plane/v1/runtime/device-config:resolve",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
        )
        request._read_bytes = b'{"device_id":"dev-001","client_id":"client-001"}'

        response = asyncio.run(handler.handle_resolve_device_config(request))
        payload = yaml.safe_load(response.text)

        assert response.status == 200
        assert payload["device"]["agent_id"] == "agent-frontdesk"
        assert payload["binding"]["mapping_id"] == "map-device-agent-001"


def test_store_creates_user_channel_and_device_agent_mappings():
    with tempfile.TemporaryDirectory() as temp_dir:
        store = LocalControlPlaneStore(Path(temp_dir))

        user = store.create_user({"user_id": "user-001", "name": "Alice"})
        channel = store.create_channel(
            {"channel_id": "channel-home", "user_id": "user-001", "name": "Home"}
        )
        mapping = store.bind_device_agent(
            {
                "mapping_id": "map-device-agent-001",
                "device_id": "dev-001",
                "agent_id": "agent-frontdesk",
            }
        )

        assert user["user_id"] == "user-001"
        assert channel["channel_id"] == "channel-home"
        assert channel["user_id"] == "user-001"
        assert mapping["agent_id"] == "agent-frontdesk"
        assert store.get_user("user-001")["name"] == "Alice"
        assert store.get_channel("channel-home")["name"] == "Home"
        assert store.get_active_device_agent_mapping("dev-001")["mapping_id"] == "map-device-agent-001"
