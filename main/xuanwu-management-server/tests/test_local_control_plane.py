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


def test_control_plane_auth_login_and_logout_issue_session():
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        handler = ControlPlaneHandler(
            {
                "server": {"auth_key": "runtime-secret"},
                "control-plane": {"data_dir": str(root)},
            }
        )
        handler.store.create_user({"user_id": "user-001", "name": "Alice", "password": "pw-001"})

        login_request = make_mocked_request(
            "POST",
            "/control-plane/v1/auth/login",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
        )
        login_request._read_bytes = b'{"user_id":"user-001","password":"pw-001"}'
        login_response = asyncio.run(handler.handle_login(login_request))
        login_payload = yaml.safe_load(login_response.text)

        logout_request = make_mocked_request(
            "POST",
            "/control-plane/v1/auth/logout",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
        )
        logout_request._read_bytes = (
            ('{"session_token":"' + login_payload["session_token"] + '"}').encode("utf-8")
        )
        logout_response = asyncio.run(handler.handle_logout(logout_request))

        assert login_response.status == 200
        assert login_payload["user_id"] == "user-001"
        assert logout_response.status == 204


def test_control_plane_auth_me_and_roles_return_effective_profile_data():
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        handler = ControlPlaneHandler(
            {
                "server": {"auth_key": "runtime-secret"},
                "control-plane": {"data_dir": str(root)},
            }
        )
        handler.store.save_role(
            "owner",
            {
                "role_id": "owner",
                "display_label": "Owner",
                "description": "Primary device owner",
                "permissions": ["devices.read", "devices.write", "alerts.read"],
            },
        )
        handler.store.save_role(
            "operator",
            {
                "role_id": "operator",
                "display_label": "Operator",
                "description": "Runs scheduled jobs and acknowledges alarms",
                "permissions": ["jobs.read", "jobs.write", "alerts.ack"],
            },
        )
        handler.store.create_user(
            {
                "user_id": "user-admin-001",
                "name": "Plant Owner",
                "display_name": "Plant Owner",
                "email": "owner@example.com",
                "avatar_url": "https://example.com/avatar.png",
                "password": "pw-owner",
                "role_ids": ["owner", "operator"],
            }
        )

        login_request = make_mocked_request(
            "POST",
            "/control-plane/v1/auth/login",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
        )
        login_request._read_bytes = b'{"user_id":"user-admin-001","password":"pw-owner"}'
        login_response = asyncio.run(handler.handle_login(login_request))
        session_token = yaml.safe_load(login_response.text)["session_token"]

        me_request = make_mocked_request(
            "GET",
            "/control-plane/v1/auth/me",
            headers={
                "X-Xuanwu-Control-Secret": "runtime-secret",
                "Authorization": f"Bearer {session_token}",
            },
        )
        roles_request = make_mocked_request(
            "GET",
            "/control-plane/v1/roles",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
        )

        me_response = asyncio.run(handler.handle_get_me(me_request))
        roles_response = asyncio.run(handler.handle_list_roles(roles_request))
        me_payload = yaml.safe_load(me_response.text)
        roles_payload = yaml.safe_load(roles_response.text)

        assert me_response.status == 200
        assert me_payload["display_name"] == "Plant Owner"
        assert me_payload["email"] == "owner@example.com"
        assert me_payload["role_ids"] == ["owner", "operator"]
        assert sorted(me_payload["permissions"]) == [
            "alerts.ack",
            "alerts.read",
            "devices.read",
            "devices.write",
            "jobs.read",
            "jobs.write",
        ]
        assert roles_response.status == 200
        assert {item["role_id"] for item in roles_payload["items"]} == {"owner", "operator"}
        assert roles_payload["items"][0]["permission_count"] >= 3


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


def test_control_plane_user_and_channel_item_crud():
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

        get_user_response = asyncio.run(
            handler.handle_get_user(
                make_mocked_request(
                    "GET",
                    "/control-plane/v1/users/user-001",
                    headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
                    match_info={"user_id": "user-001"},
                )
            )
        )
        put_user_request = make_mocked_request(
            "PUT",
            "/control-plane/v1/users/user-001",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
            match_info={"user_id": "user-001"},
        )
        put_user_request._read_bytes = b'{"name":"Alice Updated","status":"inactive"}'
        put_user_response = asyncio.run(handler.handle_put_user(put_user_request))

        get_channel_response = asyncio.run(
            handler.handle_get_channel(
                make_mocked_request(
                    "GET",
                    "/control-plane/v1/channels/channel-home",
                    headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
                    match_info={"channel_id": "channel-home"},
                )
            )
        )
        put_channel_request = make_mocked_request(
            "PUT",
            "/control-plane/v1/channels/channel-home",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
            match_info={"channel_id": "channel-home"},
        )
        put_channel_request._read_bytes = b'{"name":"Living Room","status":"inactive"}'
        put_channel_response = asyncio.run(handler.handle_put_channel(put_channel_request))

        delete_channel_response = asyncio.run(
            handler.handle_delete_channel(
                make_mocked_request(
                    "DELETE",
                    "/control-plane/v1/channels/channel-home",
                    headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
                    match_info={"channel_id": "channel-home"},
                )
            )
        )
        delete_user_response = asyncio.run(
            handler.handle_delete_user(
                make_mocked_request(
                    "DELETE",
                    "/control-plane/v1/users/user-001",
                    headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
                    match_info={"user_id": "user-001"},
                )
            )
        )

        assert get_user_response.status == 200
        assert put_user_response.status == 200
        assert get_channel_response.status == 200
        assert put_channel_response.status == 200
        assert delete_channel_response.status == 204
        assert delete_user_response.status == 204
        assert handler.store.get_channel("channel-home") is None
        assert handler.store.get_user("user-001") is None


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


def test_control_plane_agent_side_mapping_list_endpoints_return_items():
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        handler = ControlPlaneHandler(
            {
                "server": {"auth_key": "runtime-secret"},
                "control-plane": {"data_dir": str(root)},
            }
        )
        handler.store.save_agent_model_provider_mapping(
            "map-agent-provider-001",
            {"mapping_id": "map-agent-provider-001", "agent_id": "agent-frontdesk", "model_provider_id": "provider-openai-01"},
        )
        handler.store.save_agent_model_config_mapping(
            "map-agent-model-001",
            {"mapping_id": "map-agent-model-001", "agent_id": "agent-frontdesk", "model_config_id": "model-realtime-01"},
        )
        handler.store.save_agent_knowledge_mapping(
            "map-agent-knowledge-001",
            {"mapping_id": "map-agent-knowledge-001", "agent_id": "agent-frontdesk", "knowledge_id": "kb-home-ops"},
        )
        handler.store.save_agent_workflow_mapping(
            "map-agent-workflow-001",
            {"mapping_id": "map-agent-workflow-001", "agent_id": "agent-frontdesk", "workflow_id": "wf-device-escalation"},
        )

        provider_response = asyncio.run(
            handler.handle_list_agent_model_provider_mappings(
                make_mocked_request(
                    "GET",
                    "/control-plane/v1/mappings/agent-model-providers",
                    headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
                )
            )
        )
        model_response = asyncio.run(
            handler.handle_list_agent_model_config_mappings(
                make_mocked_request(
                    "GET",
                    "/control-plane/v1/mappings/agent-model-configs",
                    headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
                )
            )
        )
        knowledge_response = asyncio.run(
            handler.handle_list_agent_knowledge_mappings(
                make_mocked_request(
                    "GET",
                    "/control-plane/v1/mappings/agent-knowledge",
                    headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
                )
            )
        )
        workflow_response = asyncio.run(
            handler.handle_list_agent_workflow_mappings(
                make_mocked_request(
                    "GET",
                    "/control-plane/v1/mappings/agent-workflows",
                    headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
                )
            )
        )

        assert yaml.safe_load(provider_response.text)["items"][0]["model_provider_id"] == "provider-openai-01"
        assert yaml.safe_load(model_response.text)["items"][0]["model_config_id"] == "model-realtime-01"
        assert yaml.safe_load(knowledge_response.text)["items"][0]["knowledge_id"] == "kb-home-ops"
        assert yaml.safe_load(workflow_response.text)["items"][0]["workflow_id"] == "wf-device-escalation"


def test_control_plane_agent_side_mapping_create_endpoints_persist_records():
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        handler = ControlPlaneHandler(
            {
                "server": {"auth_key": "runtime-secret"},
                "control-plane": {"data_dir": str(root)},
            }
        )

        provider_request = make_mocked_request(
            "POST",
            "/control-plane/v1/mappings/agent-model-providers",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
        )
        provider_request._read_bytes = (
            b'{"mapping_id":"map-agent-provider-001","agent_id":"agent-frontdesk","model_provider_id":"provider-openai-01"}'
        )
        model_request = make_mocked_request(
            "POST",
            "/control-plane/v1/mappings/agent-model-configs",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
        )
        model_request._read_bytes = (
            b'{"mapping_id":"map-agent-model-001","agent_id":"agent-frontdesk","model_config_id":"model-realtime-01"}'
        )
        knowledge_request = make_mocked_request(
            "POST",
            "/control-plane/v1/mappings/agent-knowledge",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
        )
        knowledge_request._read_bytes = (
            b'{"mapping_id":"map-agent-knowledge-001","agent_id":"agent-frontdesk","knowledge_id":"kb-home-ops"}'
        )
        workflow_request = make_mocked_request(
            "POST",
            "/control-plane/v1/mappings/agent-workflows",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
        )
        workflow_request._read_bytes = (
            b'{"mapping_id":"map-agent-workflow-001","agent_id":"agent-frontdesk","workflow_id":"wf-device-escalation"}'
        )

        provider_response = asyncio.run(
            handler.handle_create_agent_model_provider_mapping(provider_request)
        )
        model_response = asyncio.run(
            handler.handle_create_agent_model_config_mapping(model_request)
        )
        knowledge_response = asyncio.run(
            handler.handle_create_agent_knowledge_mapping(knowledge_request)
        )
        workflow_response = asyncio.run(
            handler.handle_create_agent_workflow_mapping(workflow_request)
        )

        assert provider_response.status == 201
        assert model_response.status == 201
        assert knowledge_response.status == 201
        assert workflow_response.status == 201
        assert handler.store.list_agent_model_provider_mappings()[0]["model_provider_id"] == "provider-openai-01"
        assert handler.store.list_agent_model_config_mappings()[0]["model_config_id"] == "model-realtime-01"
        assert handler.store.list_agent_knowledge_mappings()[0]["knowledge_id"] == "kb-home-ops"
        assert handler.store.list_agent_workflow_mappings()[0]["workflow_id"] == "wf-device-escalation"


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


def test_control_plane_batch_import_devices_creates_records():
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        handler = ControlPlaneHandler(
            {
                "server": {"auth_key": "runtime-secret"},
                "control-plane": {"data_dir": str(root)},
            }
        )
        handler.store.create_user({"user_id": "user-001", "name": "Alice"})

        request = make_mocked_request(
            "POST",
            "/control-plane/v1/devices:batch-import",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
        )
        request._read_bytes = (
            b'{"items":['
            b'{"device_id":"dev-001","user_id":"user-001","device_type":"conversation_terminal"},'
            b'{"device_id":"dev-002","device_type":"sensor"}'
            b']}'
        )

        response = asyncio.run(handler.handle_batch_import_devices(request))
        payload = yaml.safe_load(response.text)

        assert response.status == 201
        assert payload["imported"] == 2
        assert payload["items"][0]["user_id"] == "user-001"
        assert payload["items"][1]["user_id"] == "anonymous"
        assert handler.store.get_device("dev-002")["user_id"] == "anonymous"


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


def test_control_plane_event_item_and_gateway_ingest_endpoints_work():
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        handler = ControlPlaneHandler(
            {
                "server": {"auth_key": "runtime-secret"},
                "control-plane": {"data_dir": str(root)},
            }
        )

        gateway_event_request = make_mocked_request(
            "POST",
            "/control-plane/v1/gateway/events",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
        )
        gateway_event_request._read_bytes = (
            b'{"event_id":"evt-002","event_type":"device.online","device_id":"dev-001"}'
        )
        gateway_telemetry_request = make_mocked_request(
            "POST",
            "/control-plane/v1/gateway/telemetry",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
        )
        gateway_telemetry_request._read_bytes = (
            b'{"telemetry_id":"tel-002","device_id":"dev-001","capability_code":"sensor.humidity","value":62.5}'
        )
        gateway_result_request = make_mocked_request(
            "POST",
            "/control-plane/v1/gateway/command-results",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
        )
        gateway_result_request._read_bytes = (
            b'{"result_id":"cmdr-001","device_id":"dev-001","request_id":"req-001","status":"accepted"}'
        )

        event_response = asyncio.run(handler.handle_gateway_event(gateway_event_request))
        telemetry_response = asyncio.run(handler.handle_gateway_telemetry(gateway_telemetry_request))
        command_result_response = asyncio.run(
            handler.handle_gateway_command_result(gateway_result_request)
        )
        get_event_response = asyncio.run(
            handler.handle_get_event(
                make_mocked_request(
                    "GET",
                    "/control-plane/v1/events/evt-002",
                    headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
                    match_info={"event_id": "evt-002"},
                )
            )
        )

        assert event_response.status == 201
        assert telemetry_response.status == 201
        assert command_result_response.status == 201
        assert get_event_response.status == 200
        assert yaml.safe_load(get_event_response.text)["event_id"] == "evt-002"


def test_store_filters_events_and_telemetry_by_query_dimensions():
    with tempfile.TemporaryDirectory() as temp_dir:
        store = LocalControlPlaneStore(Path(temp_dir))

        store.append_event(
            {
                "event_id": "evt-001",
                "event_type": "device.online",
                "device_id": "dev-001",
                "gateway_id": "gateway-001",
                "site_id": "site-a",
                "severity": "info",
            }
        )
        store.append_event(
            {
                "event_id": "evt-002",
                "event_type": "alarm.triggered",
                "device_id": "dev-002",
                "gateway_id": "gateway-002",
                "site_id": "site-b",
                "severity": "critical",
            }
        )
        store.append_telemetry(
            {
                "telemetry_id": "tel-001",
                "device_id": "dev-001",
                "gateway_id": "gateway-001",
                "metric_code": "sensor.temperature",
                "value": 24.8,
                "timestamp": "2026-03-30T12:00:00Z",
                "tags": {"site_id": "site-a"},
            }
        )
        store.append_telemetry(
            {
                "telemetry_id": "tel-002",
                "device_id": "dev-002",
                "gateway_id": "gateway-002",
                "metric_code": "sensor.temperature",
                "value": 30.1,
                "timestamp": "2026-03-30T12:10:00Z",
                "tags": {"site_id": "site-b"},
            }
        )

        filtered_events = store.list_events({"device_id": "dev-002", "severity": "critical"})
        filtered_telemetry = store.list_telemetry({"device_id": "dev-001", "site_id": "site-a"})

        assert [item["event_id"] for item in filtered_events] == ["evt-002"]
        assert [item["telemetry_id"] for item in filtered_telemetry] == ["tel-001"]


def test_control_plane_gateway_command_result_creates_command_result_event():
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
            "/control-plane/v1/gateway/command-results",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
        )
        request._read_bytes = (
            b'{"result_id":"cmdr-001","device_id":"dev-001","gateway_id":"gateway-001","request_id":"req-001","status":"succeeded","trace_id":"trace-001"}'
        )

        response = asyncio.run(handler.handle_gateway_command_result(request))

        assert response.status == 201
        command_event = handler.store.get_event("evt-cmdr-001")
        assert command_event["event_type"] == "command.result"
        assert command_event["payload"]["status"] == "succeeded"


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


def test_store_lists_due_schedules_and_records_job_run_lifecycle():
    with tempfile.TemporaryDirectory() as temp_dir:
        store = LocalControlPlaneStore(Path(temp_dir))

        store.save_schedule(
            "sched-telemetry-001",
            {
                "schedule_id": "sched-telemetry-001",
                "enabled": True,
                "job_type": "telemetry_rollup",
                "executor_type": "platform",
                "interval_seconds": 300,
                "next_run_at": "2026-03-31T10:00:00Z",
                "payload": {"site_id": "site-a"},
            },
        )
        store.save_schedule(
            "sched-agent-001",
            {
                "schedule_id": "sched-agent-001",
                "enabled": False,
                "job_type": "agent_run",
                "executor_type": "agent",
                "next_run_at": "2026-03-31T10:00:00Z",
                "payload": {"agent_id": "agent-001"},
            },
        )

        due_items = store.list_due_schedules("2026-03-31T10:00:00Z", limit=10)
        claimed = store.claim_schedule("sched-telemetry-001", "2026-03-31T10:00:00Z")
        completed = store.complete_job_run(
            claimed["job_run_id"],
            {
                "status": "completed",
                "result": {"site_id": "site-a", "status": "completed"},
            },
        )

        assert [item["schedule_id"] for item in due_items] == ["sched-telemetry-001"]
        assert claimed["job_type"] == "telemetry_rollup"
        assert claimed["executor_type"] == "platform"
        assert claimed["payload"]["site_id"] == "site-a"
        assert store.get_schedule("sched-telemetry-001")["next_run_at"] == "2026-03-31T10:05:00Z"
        assert completed["status"] == "completed"
        assert store.get_job_run(claimed["job_run_id"])["status"] == "completed"


def test_control_plane_job_schedule_and_run_endpoints_work_together():
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        handler = ControlPlaneHandler(
            {
                "server": {"auth_key": "runtime-secret"},
                "control-plane": {"data_dir": str(root)},
            }
        )

        create_schedule_request = make_mocked_request(
            "POST",
            "/control-plane/v1/jobs/schedules",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
        )
        create_schedule_request._read_bytes = (
            b'{"schedule_id":"sched-telemetry-001","enabled":true,"job_type":"telemetry_rollup",'
            b'"executor_type":"platform","interval_seconds":300,'
            b'"next_run_at":"2026-03-31T10:00:00Z","payload":{"site_id":"site-a"}}'
        )

        create_schedule_response = asyncio.run(
            handler.handle_create_job_schedule(create_schedule_request)
        )
        due_response = asyncio.run(
            handler.handle_list_due_job_schedules(
                make_mocked_request(
                    "GET",
                    "/control-plane/v1/jobs/schedules:due?now=2026-03-31T10:00:00Z&limit=20",
                    headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
                )
            )
        )
        claim_request = make_mocked_request(
            "POST",
            "/control-plane/v1/jobs/schedules/sched-telemetry-001:claim",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
            match_info={"schedule_id": "sched-telemetry-001"},
        )
        claim_request._read_bytes = b'{"scheduled_for":"2026-03-31T10:00:00Z"}'
        claim_response = asyncio.run(handler.handle_claim_job_schedule(claim_request))

        job_run_id = yaml.safe_load(claim_response.text)["job_run_id"]
        complete_request = make_mocked_request(
            "POST",
            f"/control-plane/v1/jobs/runs/{job_run_id}:complete",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
            match_info={"job_run_id": job_run_id},
        )
        complete_request._read_bytes = (
            b'{"status":"completed","result":{"site_id":"site-a","status":"completed"}}'
        )
        complete_response = asyncio.run(handler.handle_complete_job_run(complete_request))
        list_runs_response = asyncio.run(
            handler.handle_list_job_runs(
                make_mocked_request(
                    "GET",
                    "/control-plane/v1/jobs/runs",
                    headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
                )
            )
        )

        assert create_schedule_response.status == 201
        assert due_response.status == 200
        assert claim_response.status == 201
        assert complete_response.status == 200
        assert yaml.safe_load(list_runs_response.text)["items"][0]["status"] == "completed"


def test_control_plane_resource_item_endpoints_round_trip_real_records():
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        handler = ControlPlaneHandler(
            {
                "server": {"auth_key": "runtime-secret"},
                "control-plane": {"data_dir": str(root)},
            }
        )

        handler.store.create_user(
            {"user_id": "user-ops-001", "name": "Ops Team", "status": "active"}
        )
        handler.store.save_device(
            "dev-boiler-001",
            {
                "device_id": "dev-boiler-001",
                "user_id": "user-ops-001",
                "device_type": "industrial_controller",
                "protocol_type": "modbus_tcp",
                "site_id": "plant-a",
            },
        )
        handler.store.save_agent(
            "agent-factory-ops",
            {"agent_id": "agent-factory-ops", "name": "Factory Ops"},
        )
        handler.store.save_gateway(
            "gateway-modbus-001",
            {
                "gateway_id": "gateway-modbus-001",
                "protocol_type": "modbus_tcp",
                "site_id": "plant-a",
            },
        )
        handler.store.save_capability(
            "cap-temperature",
            {
                "capability_id": "cap-temperature",
                "capability_code": "sensor.temperature",
            },
        )
        handler.store.save_capability_route(
            "route-temperature-modbus",
            {
                "route_id": "route-temperature-modbus",
                "capability_code": "sensor.temperature",
                "gateway_id": "gateway-modbus-001",
            },
        )
        handler.store.save_firmware(
            "fw-industrial-001",
            {
                "firmware_id": "fw-industrial-001",
                "device_type": "industrial_controller",
                "version": "2.3.7",
            },
        )
        handler.store.save_ota_campaign(
            "campaign-industrial-001",
            {
                "campaign_id": "campaign-industrial-001",
                "firmware_id": "fw-industrial-001",
                "status": "scheduled",
            },
        )

        put_device_request = make_mocked_request(
            "PUT",
            "/control-plane/v1/devices/dev-boiler-001",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
            match_info={"device_id": "dev-boiler-001"},
        )
        put_device_request._read_bytes = (
            b'{"user_id":"user-ops-001","device_type":"industrial_controller",'
            b'"protocol_type":"modbus_tcp","site_id":"plant-b","display_name":"Boiler PLC"}'
        )

        put_agent_request = make_mocked_request(
            "PUT",
            "/control-plane/v1/agents/agent-factory-ops",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
            match_info={"agent_id": "agent-factory-ops"},
        )
        put_agent_request._read_bytes = (
            b'{"name":"Factory Operations Agent","status":"active"}'
        )

        put_device_response = asyncio.run(handler.handle_put_device(put_device_request))
        put_agent_response = asyncio.run(handler.handle_put_agent(put_agent_request))
        get_device_response = asyncio.run(
            handler.handle_get_device(
                make_mocked_request(
                    "GET",
                    "/control-plane/v1/devices/dev-boiler-001",
                    headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
                    match_info={"device_id": "dev-boiler-001"},
                )
            )
        )
        get_agent_response = asyncio.run(
            handler.handle_get_agent(
                make_mocked_request(
                    "GET",
                    "/control-plane/v1/agents/agent-factory-ops",
                    headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
                    match_info={"agent_id": "agent-factory-ops"},
                )
            )
        )
        list_gateway_response = asyncio.run(
            handler.handle_list_gateways(
                make_mocked_request(
                    "GET",
                    "/control-plane/v1/gateways",
                    headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
                )
            )
        )
        get_gateway_response = asyncio.run(
            handler.handle_get_gateway(
                make_mocked_request(
                    "GET",
                    "/control-plane/v1/gateways/gateway-modbus-001",
                    headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
                    match_info={"gateway_id": "gateway-modbus-001"},
                )
            )
        )
        list_capability_response = asyncio.run(
            handler.handle_list_capabilities(
                make_mocked_request(
                    "GET",
                    "/control-plane/v1/capabilities",
                    headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
                )
            )
        )
        list_route_response = asyncio.run(
            handler.handle_list_capability_routes(
                make_mocked_request(
                    "GET",
                    "/control-plane/v1/capability-routes",
                    headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
                )
            )
        )
        list_firmware_response = asyncio.run(
            handler.handle_list_firmwares(
                make_mocked_request(
                    "GET",
                    "/control-plane/v1/ota/firmwares",
                    headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
                )
            )
        )
        get_firmware_response = asyncio.run(
            handler.handle_get_firmware(
                make_mocked_request(
                    "GET",
                    "/control-plane/v1/ota/firmwares/fw-industrial-001",
                    headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
                    match_info={"firmware_id": "fw-industrial-001"},
                )
            )
        )
        list_campaign_response = asyncio.run(
            handler.handle_list_ota_campaigns(
                make_mocked_request(
                    "GET",
                    "/control-plane/v1/ota/campaigns",
                    headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
                )
            )
        )

        assert put_device_response.status == 200
        assert put_agent_response.status == 200
        assert yaml.safe_load(get_device_response.text)["site_id"] == "plant-b"
        assert yaml.safe_load(get_agent_response.text)["name"] == "Factory Operations Agent"
        assert yaml.safe_load(list_gateway_response.text)["items"][0]["gateway_id"] == "gateway-modbus-001"
        assert yaml.safe_load(get_gateway_response.text)["site_id"] == "plant-a"
        assert yaml.safe_load(list_capability_response.text)["items"][0]["capability_code"] == "sensor.temperature"
        assert yaml.safe_load(list_route_response.text)["items"][0]["route_id"] == "route-temperature-modbus"
        assert yaml.safe_load(list_firmware_response.text)["items"][0]["firmware_id"] == "fw-industrial-001"
        assert yaml.safe_load(get_firmware_response.text)["version"] == "2.3.7"
        assert yaml.safe_load(list_campaign_response.text)["items"][0]["campaign_id"] == "campaign-industrial-001"


def test_control_plane_overview_and_device_detail_endpoints_return_real_aggregates():
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        handler = ControlPlaneHandler(
            {
                "env": "staging",
                "server": {"auth_key": "runtime-secret"},
                "jobs": {"scheduler": {"poll_interval_seconds": 2}},
                "control-plane": {"data_dir": str(root)},
            }
        )

        handler.store.save_role(
            "owner",
            {
                "role_id": "owner",
                "display_label": "Owner",
                "description": "Owns devices and automations",
                "permissions": ["devices.read", "devices.write", "jobs.read", "alerts.read"],
            },
        )
        handler.store.create_user(
            {
                "user_id": "user-ops-001",
                "name": "Ops Team",
                "display_name": "Operations Team",
                "email": "ops@example.com",
                "password": "pw-ops",
                "role_ids": ["owner"],
            }
        )
        handler.store.create_channel(
            {
                "channel_id": "channel-home-001",
                "user_id": "user-ops-001",
                "name": "Home Console",
            }
        )
        handler.store.save_gateway(
            "gateway-http-001",
            {
                "gateway_id": "gateway-http-001",
                "protocol_type": "http",
                "site_id": "site-a",
                "updated_at": "2026-03-31T10:30:00Z",
            },
        )
        handler.store.save_agent(
            "agent-home-001",
            {
                "agent_id": "agent-home-001",
                "name": "Home Operations Agent",
            },
        )
        handler.store.save_device(
            "dev-living-room-001",
            {
                "device_id": "dev-living-room-001",
                "user_id": "user-ops-001",
                "device_type": "speaker_hub",
                "protocol_type": "websocket",
                "bind_status": "bound",
                "lifecycle_status": "bound",
                "gateway_id": "gateway-http-001",
                "capability_refs": ["switch.on_off", "sensor.temperature"],
                "runtime_overrides": {"voice": "calm"},
            },
        )
        handler.store.save_channel_device_mapping(
            "map-channel-device-001",
            {
                "mapping_id": "map-channel-device-001",
                "channel_id": "channel-home-001",
                "device_id": "dev-living-room-001",
                "enabled": True,
                "priority": 10,
            },
        )
        handler.store.bind_device_agent(
            {
                "mapping_id": "map-device-agent-001",
                "device_id": "dev-living-room-001",
                "agent_id": "agent-home-001",
                "enabled": True,
            }
        )
        handler.store.save_capability_route(
            "route-switch-http",
            {
                "route_id": "route-switch-http",
                "capability_code": "switch.on_off",
                "gateway_id": "gateway-http-001",
                "protocol_type": "http",
            },
        )
        handler.store.save_capability_route(
            "route-temperature-http",
            {
                "route_id": "route-temperature-http",
                "capability_code": "sensor.temperature",
                "gateway_id": "gateway-http-001",
                "protocol_type": "http",
            },
        )
        handler.store.append_event(
            {
                "event_id": "evt-alarm-001",
                "device_id": "dev-living-room-001",
                "gateway_id": "gateway-http-001",
                "event_type": "alarm.triggered",
                "alarm_id": "alarm-001",
                "severity": "critical",
                "source": "living-room-sensor",
                "message": "Temperature exceeded safe threshold",
                "occurred_at": "2026-03-31T09:50:00Z",
            }
        )
        handler.store.append_event(
            {
                "event_id": "evt-alarm-002",
                "device_id": "dev-living-room-001",
                "gateway_id": "gateway-http-001",
                "event_type": "alarm.escalated",
                "alarm_id": "alarm-001",
                "severity": "critical",
                "source": "living-room-sensor",
                "message": "Temperature alarm escalated",
                "occurred_at": "2026-03-31T10:05:00Z",
            }
        )
        handler.store.append_event(
            {
                "event_id": "evt-device-001",
                "device_id": "dev-living-room-001",
                "event_type": "device.online",
                "severity": "info",
                "occurred_at": "2026-03-31T10:15:00Z",
                "message": "Device came online",
            }
        )
        handler.store.append_telemetry(
            {
                "telemetry_id": "tel-temp-001",
                "device_id": "dev-living-room-001",
                "capability_code": "sensor.temperature",
                "value": 31.8,
                "observed_at": "2026-03-31T10:12:00Z",
            }
        )
        handler.store.append_telemetry(
            {
                "telemetry_id": "tel-switch-001",
                "device_id": "dev-living-room-001",
                "capability_code": "switch.on_off",
                "value": "on",
                "observed_at": "2026-03-31T10:13:00Z",
            }
        )
        handler.store.save_schedule(
            "sched-home-rollup-001",
            {
                "schedule_id": "sched-home-rollup-001",
                "enabled": True,
                "job_type": "telemetry_rollup",
                "executor_type": "platform",
                "interval_seconds": 300,
                "next_run_at": "2026-03-31T10:00:00Z",
                "payload": {"site_id": "site-a"},
            },
        )
        handler.store.save_schedule(
            "sched-gateway-command-001",
            {
                "schedule_id": "sched-gateway-command-001",
                "enabled": True,
                "job_type": "device_command",
                "executor_type": "gateway",
                "interval_seconds": 600,
                "next_run_at": "2026-03-31T10:20:00Z",
                "payload": {"device_id": "dev-living-room-001", "command": "switch.off"},
            },
        )
        queued_run = handler.store.claim_schedule("sched-home-rollup-001", "2026-03-31T10:00:00Z")
        failed_run = handler.store.claim_schedule("sched-gateway-command-001", "2026-03-31T10:20:00Z")
        handler.store.fail_job_run(
            failed_run["job_run_id"],
            {
                "status": "failed",
                "error": {"code": "gateway_timeout", "message": "Gateway did not respond"},
            },
        )

        headers = {"X-Xuanwu-Control-Secret": "runtime-secret"}
        overview_response = asyncio.run(
            handler.handle_get_dashboard_overview(
                make_mocked_request("GET", "/control-plane/v1/dashboard/overview", headers=headers)
            )
        )
        portal_config_response = asyncio.run(
            handler.handle_get_portal_config(
                make_mocked_request("GET", "/control-plane/v1/portal/config", headers=headers)
            )
        )
        jobs_overview_response = asyncio.run(
            handler.handle_get_jobs_overview(
                make_mocked_request("GET", "/control-plane/v1/jobs/overview", headers=headers)
            )
        )
        alerts_overview_response = asyncio.run(
            handler.handle_get_alerts_overview(
                make_mocked_request("GET", "/control-plane/v1/alerts/overview", headers=headers)
            )
        )
        device_detail_response = asyncio.run(
            handler.handle_get_device_detail(
                make_mocked_request(
                    "GET",
                    "/control-plane/v1/devices/dev-living-room-001/detail",
                    headers=headers,
                    match_info={"device_id": "dev-living-room-001"},
                )
            )
        )
        gateway_overview_response = asyncio.run(
            handler.handle_get_gateway_overview(
                make_mocked_request("GET", "/control-plane/v1/gateway/overview", headers=headers)
            )
        )

        overview_payload = yaml.safe_load(overview_response.text)
        portal_config_payload = yaml.safe_load(portal_config_response.text)
        jobs_overview_payload = yaml.safe_load(jobs_overview_response.text)
        alerts_overview_payload = yaml.safe_load(alerts_overview_response.text)
        device_detail_payload = yaml.safe_load(device_detail_response.text)
        gateway_overview_payload = yaml.safe_load(gateway_overview_response.text)

        assert overview_response.status == 200
        assert overview_payload["summary"]["device_count"] == 1
        assert overview_payload["summary"]["gateway_count"] == 1
        assert overview_payload["activity"][0]["event_id"] == "evt-device-001"
        assert overview_payload["gateway_summary"]["protocol_distribution"]["http"] == 1

        assert portal_config_response.status == 200
        assert portal_config_payload["product"]["name"] == "XuanWu Portal"
        assert portal_config_payload["navigation"]["primary_tabs"] == [
            "overview",
            "devices",
            "agents",
            "jobs",
            "alerts",
        ]
        assert portal_config_payload["environment"]["marker"] == "staging"

        assert jobs_overview_response.status == 200
        assert jobs_overview_payload["scheduler_health"]["enabled_schedule_count"] == 2
        assert jobs_overview_payload["running_count"] == 1
        assert jobs_overview_payload["recent_failures"][0]["job_run_id"] == failed_run["job_run_id"]
        assert jobs_overview_payload["executor_distribution"] == {"platform": 1, "gateway": 1}

        assert alerts_overview_response.status == 200
        assert alerts_overview_payload["severity_counts"]["critical"] == 1
        assert alerts_overview_payload["ack_pending_count"] == 1
        assert alerts_overview_payload["escalated_today"] == 1
        assert alerts_overview_payload["top_active_sources"][0]["source"] == "living-room-sensor"

        assert device_detail_response.status == 200
        assert device_detail_payload["owner_summary"]["user_id"] == "user-ops-001"
        assert device_detail_payload["agent_binding"]["mapping"]["agent_id"] == "agent-home-001"
        assert device_detail_payload["runtime_binding_view"]["channel_id"] == "channel-home-001"
        assert device_detail_payload["capability_routing_view"]["command_routes"][0]["gateway_id"] == "gateway-http-001"
        assert {item["capability_code"] for item in device_detail_payload["latest_telemetry_snapshot"]} == {
            "sensor.temperature",
            "switch.on_off",
        }

        assert gateway_overview_response.status == 200
        assert gateway_overview_payload["total_count"] == 1
        assert gateway_overview_payload["protocol_distribution"]["http"] == 1


def test_control_plane_job_and_alarm_detail_endpoints_return_real_records():
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        handler = ControlPlaneHandler(
            {
                "server": {"auth_key": "runtime-secret"},
                "control-plane": {"data_dir": str(root)},
            }
        )

        handler.store.save_schedule(
            "sched-nightly-001",
            {
                "schedule_id": "sched-nightly-001",
                "job_type": "alarm_escalation",
                "executor_type": "platform",
                "enabled": True,
                "cron": "0 */5 * * *",
                "timezone": "Asia/Shanghai",
                "next_run_at": "2026-03-31T18:00:00Z",
                "payload": {"site_id": "site-sh-01"},
            },
        )
        claimed = handler.store.claim_schedule("sched-nightly-001", "2026-03-31T18:00:00Z")
        handler.store.complete_job_run(
            claimed["job_run_id"],
            {
                "status": "completed",
                "result": {
                    "status": "completed",
                    "executor_type": "platform",
                    "details": {"escalated_alarm_count": 2},
                },
            },
        )
        handler.store.append_event(
            {
                "event_id": "evt-alarm-detail-001",
                "device_id": "dev-alarm-001",
                "gateway_id": "gateway-http-001",
                "event_type": "alarm.triggered",
                "alarm_id": "alarm-detail-001",
                "severity": "warning",
                "source": "warehouse-sensor",
                "message": "Humidity threshold exceeded",
                "occurred_at": "2026-03-31T18:05:00Z",
            }
        )

        headers = {"X-Xuanwu-Control-Secret": "runtime-secret"}
        schedule_response = asyncio.run(
            handler.handle_get_job_schedule(
                make_mocked_request(
                    "GET",
                    "/control-plane/v1/jobs/schedules/sched-nightly-001",
                    headers=headers,
                    match_info={"schedule_id": "sched-nightly-001"},
                )
            )
        )
        job_run_response = asyncio.run(
            handler.handle_get_job_run(
                make_mocked_request(
                    "GET",
                    f"/control-plane/v1/jobs/runs/{claimed['job_run_id']}",
                    headers=headers,
                    match_info={"job_run_id": claimed["job_run_id"]},
                )
            )
        )
        alarm_response = asyncio.run(
            handler.handle_get_alarm(
                make_mocked_request(
                    "GET",
                    "/control-plane/v1/alarms/alarm-detail-001",
                    headers=headers,
                    match_info={"alarm_id": "alarm-detail-001"},
                )
            )
        )

        schedule_payload = yaml.safe_load(schedule_response.text)
        job_run_payload = yaml.safe_load(job_run_response.text)
        alarm_payload = yaml.safe_load(alarm_response.text)

        assert schedule_response.status == 200
        assert schedule_payload["schedule_id"] == "sched-nightly-001"
        assert schedule_payload["executor_type"] == "platform"
        assert schedule_payload["payload"]["site_id"] == "site-sh-01"

        assert job_run_response.status == 200
        assert job_run_payload["job_run_id"] == claimed["job_run_id"]
        assert job_run_payload["status"] == "completed"
        assert job_run_payload["result"]["details"]["escalated_alarm_count"] == 2

        assert alarm_response.status == 200
        assert alarm_payload["alarm_id"] == "alarm-detail-001"
        assert alarm_payload["source"] == "warehouse-sensor"
        assert alarm_payload["message"] == "Humidity threshold exceeded"
        assert alarm_payload["status"] == "active"


def test_control_plane_returns_expected_errors_for_invalid_management_requests():
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        handler = ControlPlaneHandler(
            {
                "server": {"auth_key": "runtime-secret"},
                "control-plane": {"data_dir": str(root)},
            }
        )

        login_request = make_mocked_request(
            "POST",
            "/control-plane/v1/auth/login",
            headers={"X-Xuanwu-Control-Secret": "wrong-secret"},
        )
        login_request._read_bytes = b'{"user_id":"user-ops-001","password":"pw-001"}'
        bad_gateway_request = make_mocked_request(
            "POST",
            "/control-plane/v1/gateways",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
            match_info={"gateway_id": "gateway-invalid"},
        )
        bad_gateway_request._read_bytes = b'{"gateway_id":"gateway-invalid"'
        bad_batch_request = make_mocked_request(
            "POST",
            "/control-plane/v1/devices:batch-import",
            headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
        )
        bad_batch_request._read_bytes = b'{"source":"ops_console"}'

        login_response = asyncio.run(handler.handle_login(login_request))
        bad_gateway_response = asyncio.run(handler.handle_upsert_gateway(bad_gateway_request))
        bad_batch_response = asyncio.run(handler.handle_batch_import_devices(bad_batch_request))
        missing_user_response = asyncio.run(
            handler.handle_get_user(
                make_mocked_request(
                    "GET",
                    "/control-plane/v1/users/user-missing",
                    headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
                    match_info={"user_id": "user-missing"},
                )
            )
        )
        missing_device_response = asyncio.run(
            handler.handle_get_device(
                make_mocked_request(
                    "GET",
                    "/control-plane/v1/devices/dev-missing",
                    headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
                    match_info={"device_id": "dev-missing"},
                )
            )
        )
        missing_event_response = asyncio.run(
            handler.handle_get_event(
                make_mocked_request(
                    "GET",
                    "/control-plane/v1/events/evt-missing",
                    headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
                    match_info={"event_id": "evt-missing"},
                )
            )
        )
        missing_gateway_response = asyncio.run(
            handler.handle_get_gateway(
                make_mocked_request(
                    "GET",
                    "/control-plane/v1/gateways/gateway-missing",
                    headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
                    match_info={"gateway_id": "gateway-missing"},
                )
            )
        )
        missing_firmware_response = asyncio.run(
            handler.handle_get_firmware(
                make_mocked_request(
                    "GET",
                    "/control-plane/v1/ota/firmwares/fw-missing",
                    headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
                    match_info={"firmware_id": "fw-missing"},
                )
            )
        )
        missing_alarm_response = asyncio.run(
            handler.handle_ack_alarm(
                make_mocked_request(
                    "POST",
                    "/control-plane/v1/alarms/alarm-missing:ack",
                    headers={"X-Xuanwu-Control-Secret": "runtime-secret"},
                    match_info={"alarm_id": "alarm-missing"},
                )
            )
        )

        assert login_response.status == 401
        assert yaml.safe_load(login_response.text)["error"] == "control_secret_invalid"
        assert bad_gateway_response.status == 400
        assert yaml.safe_load(bad_gateway_response.text)["error"] == "invalid_json"
        assert bad_batch_response.status == 400
        assert yaml.safe_load(bad_batch_response.text)["error"] == "items_required"
        assert missing_user_response.status == 404
        assert yaml.safe_load(missing_user_response.text)["error"] == "user_not_found"
        assert missing_device_response.status == 404
        assert yaml.safe_load(missing_device_response.text)["error"] == "device_not_found"
        assert missing_event_response.status == 404
        assert yaml.safe_load(missing_event_response.text)["error"] == "event_not_found"
        assert missing_gateway_response.status == 404
        assert yaml.safe_load(missing_gateway_response.text)["error"] == "gateway_not_found"
        assert missing_firmware_response.status == 404
        assert yaml.safe_load(missing_firmware_response.text)["error"] == "firmware_not_found"
        assert missing_alarm_response.status == 404
        assert yaml.safe_load(missing_alarm_response.text)["error"] == "alarm_not_found"
