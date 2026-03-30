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


def test_control_plane_create_device_defaults_to_anonymous_user():
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
            "/control-plane/v1/devices",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
        )
        request._read_bytes = (
            b'{"device_id":"dev-anon-001","device_type":"conversation_terminal","protocol_type":"websocket"}'
        )

        response = asyncio.run(handler.handle_create_device(request))
        payload = yaml.safe_load(response.text)

        assert response.status == 201
        assert payload["device_id"] == "dev-anon-001"
        assert payload["user_id"] == "anonymous"
        assert handler.store.get_device("dev-anon-001")["user_id"] == "anonymous"
        assert handler.store.get_user("anonymous")["is_anonymous"] is True


def test_control_plane_rejects_device_with_unknown_user():
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
            "/control-plane/v1/devices",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
        )
        request._read_bytes = (
            b'{"device_id":"dev-user-404","user_id":"user-404","device_type":"conversation_terminal"}'
        )

        response = asyncio.run(handler.handle_create_device(request))
        payload = yaml.safe_load(response.text)

        assert response.status == 400
        assert payload["error"] == "user_not_found"


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


def test_control_plane_create_channel_defaults_to_anonymous_user():
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
            "/control-plane/v1/channels",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
        )
        request._read_bytes = b'{"channel_id":"channel-anon-001","name":"Anonymous Room"}'

        response = asyncio.run(handler.handle_create_channel(request))
        payload = yaml.safe_load(response.text)

        assert response.status == 201
        assert payload["user_id"] == "anonymous"
        assert handler.store.get_channel("channel-anon-001")["user_id"] == "anonymous"
        assert handler.store.get_user("anonymous")["is_anonymous"] is True


def test_store_lists_devices_and_defaults_anonymous_user():
    with tempfile.TemporaryDirectory() as temp_dir:
        store = LocalControlPlaneStore(Path(temp_dir))

        store.save_device(
            "dev-001",
            {
                "device_id": "dev-001",
                "device_type": "conversation_terminal",
            },
        )

        devices = store.list_devices()

        assert len(devices) == 1
        assert devices[0]["device_id"] == "dev-001"
        assert devices[0]["user_id"] == "anonymous"
        assert store.get_user("anonymous")["is_anonymous"] is True


def test_control_plane_mapping_endpoints_persist_and_list_records():
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        handler = ControlPlaneHandler(
            {
                "server": {"auth_key": "runtime-secret"},
                "control-plane": {"data_dir": str(root)},
            }
        )

        handler.store.create_user({"user_id": "user-001", "name": "Alice"})
        handler.store.create_channel(
            {"channel_id": "channel-home", "user_id": "user-001", "name": "Home"}
        )
        handler.store.save_device(
            "dev-001",
            {
                "device_id": "dev-001",
                "user_id": "user-001",
                "device_type": "conversation_terminal",
            },
        )

        channel_device_request = make_mocked_request(
            "POST",
            "/control-plane/v1/mappings/channel-devices",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
        )
        channel_device_request._read_bytes = (
            b'{"mapping_id":"map-channel-device-001","channel_id":"channel-home","device_id":"dev-001"}'
        )

        device_agent_request = make_mocked_request(
            "POST",
            "/control-plane/v1/mappings/device-agents",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
        )
        device_agent_request._read_bytes = (
            b'{"mapping_id":"map-device-agent-001","device_id":"dev-001","agent_id":"agent-frontdesk"}'
        )

        channel_device_response = asyncio.run(
            handler.handle_create_channel_device_mapping(channel_device_request)
        )
        device_agent_response = asyncio.run(
            handler.handle_create_device_agent_mapping(device_agent_request)
        )

        user_devices_response = asyncio.run(
            handler.handle_list_user_device_mappings(
                make_mocked_request(
                    "GET",
                    "/control-plane/v1/mappings/user-devices",
                    headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
                )
            )
        )
        user_channels_response = asyncio.run(
            handler.handle_list_user_channel_mappings(
                make_mocked_request(
                    "GET",
                    "/control-plane/v1/mappings/user-channels",
                    headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
                )
            )
        )
        channel_devices_response = asyncio.run(
            handler.handle_list_channel_device_mappings(
                make_mocked_request(
                    "GET",
                    "/control-plane/v1/mappings/channel-devices",
                    headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
                )
            )
        )
        device_agents_response = asyncio.run(
            handler.handle_list_device_agent_mappings(
                make_mocked_request(
                    "GET",
                    "/control-plane/v1/mappings/device-agents",
                    headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
                )
            )
        )

        assert channel_device_response.status == 201
        assert device_agent_response.status == 201
        assert yaml.safe_load(user_devices_response.text)["items"][0]["device_id"] == "dev-001"
        assert yaml.safe_load(user_channels_response.text)["items"][0]["channel_id"] == "channel-home"
        assert yaml.safe_load(channel_devices_response.text)["items"][0]["mapping_id"] == "map-channel-device-001"
        assert yaml.safe_load(device_agents_response.text)["items"][0]["agent_id"] == "agent-frontdesk"


def test_control_plane_runtime_views_return_binding_and_capability_routes():
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        handler = ControlPlaneHandler(
            {
                "server": {"auth_key": "runtime-secret"},
                "control-plane": {"data_dir": str(root)},
            }
        )

        handler.store.create_user({"user_id": "user-001", "name": "Alice"})
        handler.store.create_channel(
            {"channel_id": "channel-home", "user_id": "user-001", "name": "Home"}
        )
        handler.store.save_device(
            "dev-001",
            {
                "device_id": "dev-001",
                "user_id": "user-001",
                "device_type": "conversation_terminal",
                "gateway_id": "gateway-http-001",
                "capability_refs": ["switch.on_off"],
            },
        )
        handler.store.save_channel_device_mapping(
            "map-channel-device-001",
            {
                "mapping_id": "map-channel-device-001",
                "channel_id": "channel-home",
                "device_id": "dev-001",
            },
        )
        handler.store.bind_device_agent(
            {
                "mapping_id": "map-device-agent-001",
                "device_id": "dev-001",
                "agent_id": "agent-frontdesk",
            }
        )
        handler.store.save_gateway(
            "gateway-http-001",
            {
                "gateway_id": "gateway-http-001",
                "protocol_type": "http",
            },
        )
        handler.store.save_capability_route(
            "route-switch-http-001",
            {
                "route_id": "route-switch-http-001",
                "capability_code": "switch.on_off",
                "gateway_id": "gateway-http-001",
                "protocol_type": "http",
            },
        )

        binding_response = asyncio.run(
            handler.handle_get_runtime_binding_view(
                make_mocked_request(
                    "GET",
                    "/control-plane/v1/runtime/devices/dev-001/binding-view",
                    headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
                    match_info={"device_id": "dev-001"},
                )
            )
        )
        capability_routing_response = asyncio.run(
            handler.handle_get_runtime_capability_routing_view(
                make_mocked_request(
                    "GET",
                    "/control-plane/v1/runtime/devices/dev-001/capability-routing-view",
                    headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
                    match_info={"device_id": "dev-001"},
                )
            )
        )

        assert binding_response.status == 200
        assert capability_routing_response.status == 200
        binding_payload = yaml.safe_load(binding_response.text)
        capability_payload = yaml.safe_load(capability_routing_response.text)
        assert binding_payload["device_id"] == "dev-001"
        assert binding_payload["channel_id"] == "channel-home"
        assert binding_payload["agent_id"] == "agent-frontdesk"
        assert capability_payload["device_id"] == "dev-001"
        assert capability_payload["command_routes"][0]["gateway_id"] == "gateway-http-001"
        assert capability_payload["command_routes"][0]["capability_code"] == "switch.on_off"


def test_control_plane_device_lifecycle_claim_bind_suspend_and_retire():
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        handler = ControlPlaneHandler(
            {
                "server": {"auth_key": "runtime-secret"},
                "control-plane": {"data_dir": str(root)},
            }
        )

        handler.store.create_user({"user_id": "user-001", "name": "Alice"})
        handler.store.save_device(
            "dev-001",
            {
                "device_id": "dev-001",
                "device_type": "conversation_terminal",
                "bind_code": "654321",
            },
        )

        claim_request = make_mocked_request(
            "POST",
            "/control-plane/v1/devices/dev-001:claim",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
            match_info={"device_id": "dev-001"},
        )
        claim_request._read_bytes = b'{"user_id":"user-001"}'

        bind_request = make_mocked_request(
            "POST",
            "/control-plane/v1/devices/dev-001:bind",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
            match_info={"device_id": "dev-001"},
        )
        bind_request._read_bytes = b'{"bind_code":"654321"}'

        suspend_request = make_mocked_request(
            "POST",
            "/control-plane/v1/devices/dev-001:suspend",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
            match_info={"device_id": "dev-001"},
        )
        suspend_request._read_bytes = b'{"reason":"maintenance_window"}'

        retire_request = make_mocked_request(
            "POST",
            "/control-plane/v1/devices/dev-001:retire",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
            match_info={"device_id": "dev-001"},
        )
        retire_request._read_bytes = b'{"reason":"hardware_replaced"}'

        claim_response = asyncio.run(handler.handle_claim_device(claim_request))
        bind_response = asyncio.run(handler.handle_bind_device(bind_request))
        suspend_response = asyncio.run(handler.handle_suspend_device(suspend_request))
        retire_response = asyncio.run(handler.handle_retire_device(retire_request))

        assert claim_response.status == 200
        assert bind_response.status == 200
        assert suspend_response.status == 200
        assert retire_response.status == 200

        device = handler.store.get_device("dev-001")
        assert device["user_id"] == "user-001"
        assert device["lifecycle_status"] == "retired"
        assert device["bind_status"] == "bound"
        assert device["suspend_reason"] == "maintenance_window"
        assert device["retire_reason"] == "hardware_replaced"


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
        device = store.save_device(
            "dev-001",
            {
                "device_id": "dev-001",
                "user_id": "user-001",
                "device_type": "conversation_terminal",
            },
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
        assert device["user_id"] == "user-001"
        assert mapping["agent_id"] == "agent-frontdesk"
        assert store.get_user("user-001")["name"] == "Alice"
        assert store.get_channel("channel-home")["name"] == "Home"
        assert store.get_active_device_agent_mapping("dev-001")["mapping_id"] == "map-device-agent-001"


def test_store_persists_events_telemetry_and_active_alarm_state():
    with tempfile.TemporaryDirectory() as temp_dir:
        store = LocalControlPlaneStore(Path(temp_dir))

        event = store.append_event(
            {
                "event_id": "evt-001",
                "event_type": "alarm.triggered",
                "device_id": "dev-001",
                "alarm_id": "alarm-001",
                "message": "temperature high",
            }
        )
        telemetry = store.append_telemetry(
            {
                "telemetry_id": "tel-001",
                "device_id": "dev-001",
                "capability_code": "sensor.temperature",
                "value": 31.5,
            }
        )

        assert event["event_id"] == "evt-001"
        assert telemetry["telemetry_id"] == "tel-001"
        assert store.list_events()[0]["event_type"] == "alarm.triggered"
        assert store.list_telemetry()[0]["capability_code"] == "sensor.temperature"
        assert store.list_alarms()[0]["alarm_id"] == "alarm-001"


def test_control_plane_event_telemetry_and_alarm_endpoints_work_together():
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        handler = ControlPlaneHandler(
            {
                "server": {"auth_key": "runtime-secret"},
                "control-plane": {"data_dir": str(root)},
            }
        )

        event_request = make_mocked_request(
            "POST",
            "/control-plane/v1/events",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
        )
        event_request._read_bytes = (
            b'{"event_id":"evt-001","event_type":"alarm.triggered","device_id":"dev-001","alarm_id":"alarm-001","message":"temperature high"}'
        )

        telemetry_request = make_mocked_request(
            "POST",
            "/control-plane/v1/telemetry",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
        )
        telemetry_request._read_bytes = (
            b'{"telemetry_id":"tel-001","device_id":"dev-001","capability_code":"sensor.temperature","value":31.5}'
        )

        event_response = asyncio.run(handler.handle_post_event(event_request))
        telemetry_response = asyncio.run(handler.handle_post_telemetry(telemetry_request))
        alarms_response = asyncio.run(
            handler.handle_list_alarms(
                make_mocked_request(
                    "GET",
                    "/control-plane/v1/alarms",
                    headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
                )
            )
        )

        assert event_response.status == 201
        assert telemetry_response.status == 201
        assert alarms_response.status == 200
        assert yaml.safe_load(alarms_response.text)["items"][0]["alarm_id"] == "alarm-001"


def test_store_persists_gateway_capability_route_and_ota_records():
    with tempfile.TemporaryDirectory() as temp_dir:
        store = LocalControlPlaneStore(Path(temp_dir))

        gateway = store.save_gateway(
            "gateway-http-001",
            {"gateway_id": "gateway-http-001", "protocol_type": "http", "name": "HTTP Gateway"},
        )
        capability = store.save_capability(
            "cap-switch-on-off",
            {"capability_id": "cap-switch-on-off", "capability_code": "switch.on_off"},
        )
        route = store.save_capability_route(
            "route-switch-http-001",
            {
                "route_id": "route-switch-http-001",
                "capability_code": "switch.on_off",
                "gateway_id": "gateway-http-001",
            },
        )
        firmware = store.save_firmware(
            "fw-esp32-001",
            {"firmware_id": "fw-esp32-001", "device_type": "conversation_terminal", "version": "1.0.0"},
        )
        campaign = store.save_ota_campaign(
            "campaign-001",
            {"campaign_id": "campaign-001", "firmware_id": "fw-esp32-001", "status": "draft"},
        )

        assert gateway["gateway_id"] == "gateway-http-001"
        assert capability["capability_code"] == "switch.on_off"
        assert route["gateway_id"] == "gateway-http-001"
        assert firmware["firmware_id"] == "fw-esp32-001"
        assert campaign["campaign_id"] == "campaign-001"
        assert store.list_gateways()[0]["protocol_type"] == "http"
        assert store.list_capabilities()[0]["capability_code"] == "switch.on_off"
        assert store.list_capability_routes()[0]["route_id"] == "route-switch-http-001"
        assert store.list_firmwares()[0]["firmware_id"] == "fw-esp32-001"
        assert store.list_ota_campaigns()[0]["campaign_id"] == "campaign-001"


def test_control_plane_gateway_capability_and_ota_endpoints_work_together():
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        handler = ControlPlaneHandler(
            {
                "server": {"auth_key": "runtime-secret"},
                "control-plane": {"data_dir": str(root)},
            }
        )

        gateway_request = make_mocked_request(
            "POST",
            "/control-plane/v1/gateways",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
            match_info={"gateway_id": "gateway-http-001"},
        )
        gateway_request._read_bytes = (
            b'{"gateway_id":"gateway-http-001","protocol_type":"http","name":"HTTP Gateway"}'
        )

        capability_request = make_mocked_request(
            "POST",
            "/control-plane/v1/capabilities",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
        )
        capability_request._read_bytes = (
            b'{"capability_id":"cap-switch-on-off","capability_code":"switch.on_off"}'
        )

        route_request = make_mocked_request(
            "POST",
            "/control-plane/v1/capability-routes",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
        )
        route_request._read_bytes = (
            b'{"route_id":"route-switch-http-001","capability_code":"switch.on_off","gateway_id":"gateway-http-001"}'
        )

        firmware_request = make_mocked_request(
            "POST",
            "/control-plane/v1/ota/firmwares",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
        )
        firmware_request._read_bytes = (
            b'{"firmware_id":"fw-esp32-001","device_type":"conversation_terminal","version":"1.0.0"}'
        )

        campaign_request = make_mocked_request(
            "POST",
            "/control-plane/v1/ota/campaigns",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
        )
        campaign_request._read_bytes = (
            b'{"campaign_id":"campaign-001","firmware_id":"fw-esp32-001","status":"draft"}'
        )

        gateway_response = asyncio.run(handler.handle_upsert_gateway(gateway_request))
        capability_response = asyncio.run(handler.handle_create_capability(capability_request))
        route_response = asyncio.run(handler.handle_create_capability_route(route_request))
        firmware_response = asyncio.run(handler.handle_upsert_firmware(firmware_request))
        campaign_response = asyncio.run(handler.handle_create_ota_campaign(campaign_request))

        assert gateway_response.status == 200
        assert capability_response.status == 201
        assert route_response.status == 201
        assert firmware_response.status == 200
        assert campaign_response.status == 201
        assert handler.store.list_gateways()[0]["gateway_id"] == "gateway-http-001"
        assert handler.store.list_capabilities()[0]["capability_code"] == "switch.on_off"
        assert handler.store.list_firmwares()[0]["firmware_id"] == "fw-esp32-001"
