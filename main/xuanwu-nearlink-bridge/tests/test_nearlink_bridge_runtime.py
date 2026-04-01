import asyncio
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys


def _load_runtime_module():
    root = Path(__file__).resolve().parents[3]
    module_path = root / "main" / "xuanwu-nearlink-bridge" / "core" / "runtime.py"
    service_root = module_path.parents[2]
    while str(service_root) in sys.path:
        sys.path.remove(str(service_root))
    sys.path.insert(0, str(service_root))
    for name in list(sys.modules):
        if name == "config" or name.startswith("config."):
            sys.modules.pop(name, None)
        if name == "core" or name.startswith("core."):
            sys.modules.pop(name, None)
    spec = spec_from_file_location("xuanwu_nearlink_bridge_runtime_test", module_path)
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class _FakeCallbackClient:
    def __init__(self):
        self.http_push = []
        self.bridge_events = []
        self.command_results = []

    async def post_http_push(self, payload: dict):
        self.http_push.append(payload)
        return payload

    async def post_bridge_event(self, payload: dict):
        self.bridge_events.append(payload)
        return payload

    async def post_command_result(self, payload: dict):
        self.command_results.append(payload)
        return payload


def _config() -> dict:
    return {
        "bridge": {
            "bridge_id": "nearlink-bridge-test",
            "discovery": {"default_timeout_seconds": 5},
            "sessions": {"max_active_devices": 5},
            "demo": {"enabled": True, "device_prefix": "XW-NL"},
        },
        "gateway": {},
    }


def test_runtime_discovery_connect_command_query_and_disconnect():
    callback = _FakeCallbackClient()
    runtime = _load_runtime_module().NearlinkBridgeRuntime(_config(), callback_client=callback)

    discovery = asyncio.run(runtime.start_discovery({"filters": {"name_prefix": "XW-NL"}}))
    assert discovery["devices"]
    device_key = discovery["devices"][0]["device_key"]

    session = asyncio.run(runtime.connect_device(device_key))
    assert session["status"] == "connected"

    command = asyncio.run(
        runtime.command_device(
            device_key,
            {
                "device_id": "device-nearlink-001",
                "gateway_id": "gateway-nearlink-001",
                "command_type": "capability.invoke",
                "capability_code": "switch.on_off",
                "action": "turn_on",
                "arguments": {"target_state": "active"},
            },
        )
    )
    assert command["state"]["target_state"] == "active"
    assert callback.command_results[0]["adapter_type"] == "nearlink"

    query = asyncio.run(
        runtime.query_state(
            device_key,
            {
                "device_id": "device-nearlink-001",
                "gateway_id": "gateway-nearlink-001",
            },
        )
    )
    assert query["state"]["online"] is True
    assert callback.http_push[0]["protocol_type"] == "nearlink"

    disconnect = asyncio.run(runtime.disconnect_device(device_key))
    assert disconnect["status"] == "disconnected"
    assert callback.bridge_events[-1]["payload"]["online"] is False
