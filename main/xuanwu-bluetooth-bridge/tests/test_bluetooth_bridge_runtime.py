import asyncio
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys


def _load_runtime_module():
    root = Path(__file__).resolve().parents[3]
    module_path = root / "main" / "xuanwu-bluetooth-bridge" / "core" / "runtime.py"
    service_root = module_path.parents[2]
    while str(service_root) in sys.path:
        sys.path.remove(str(service_root))
    sys.path.insert(0, str(service_root))
    for name in list(sys.modules):
        if name == "config" or name.startswith("config."):
            sys.modules.pop(name, None)
        if name == "core" or name.startswith("core."):
            sys.modules.pop(name, None)
    spec = spec_from_file_location("xuanwu_bluetooth_bridge_runtime_test", module_path)
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
            "bridge_id": "bluetooth-bridge-test",
            "scan": {"default_timeout_seconds": 8, "max_concurrent_scans": 2},
            "connections": {"max_active_devices": 5},
            "demo": {"enabled": True, "device_prefix": "XW-BLE"},
        },
        "gateway": {},
    }


def test_runtime_scan_connect_read_write_and_subscribe_flow():
    callback = _FakeCallbackClient()
    runtime = _load_runtime_module().BluetoothBridgeRuntime(_config(), callback_client=callback)

    scan = asyncio.run(runtime.start_scan({"filters": {"name_prefix": "XW-BLE"}}))
    assert scan["devices"]
    device_key = scan["devices"][0]["device_key"]

    connection = asyncio.run(runtime.connect_device(device_key))
    assert connection["status"] == "connected"

    read = runtime.read_characteristic(
        device_key,
        {"service_uuid": "180f", "characteristic_uuid": "2a19", "encoding": "uint8"},
    )
    assert read["value"] == 87

    write = asyncio.run(
        runtime.write_characteristic(
            device_key,
            {
                "device_id": "device-ble-001",
                "gateway_id": "gateway-bridge-001",
                "service_uuid": "180f",
                "characteristic_uuid": "2a19",
                "encoding": "uint8",
                "value": 44,
            },
        )
    )
    assert write["value"] == 44
    assert callback.command_results[0]["adapter_type"] == "bluetooth"

    subscription = asyncio.run(
        runtime.subscribe_characteristic(
            device_key,
            {
                "device_id": "device-ble-001",
                "gateway_id": "gateway-bridge-001",
                "service_uuid": "180f",
                "characteristic_uuid": "2a19",
                "encoding": "uint8",
            },
        )
    )
    assert subscription["device_key"] == device_key
    assert callback.http_push[0]["protocol_type"] == "bluetooth"

    unsubscribe = runtime.unsubscribe_characteristic(
        device_key,
        {"service_uuid": "180f", "characteristic_uuid": "2a19"},
    )
    assert unsubscribe["status"] == "unsubscribed"

    disconnect = asyncio.run(runtime.disconnect_device(device_key))
    assert disconnect["status"] == "disconnected"
    assert callback.bridge_events[-1]["event_type"] == "bluetooth.device.disconnected"
