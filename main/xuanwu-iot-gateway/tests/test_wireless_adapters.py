from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys


def _load_module(module_name, relative_path):
    root = Path(__file__).resolve().parents[3]
    module_path = root / "main" / "xuanwu-iot-gateway" / "core" / "adapters" / relative_path
    service_root = module_path.parents[2]

    while str(service_root) in sys.path:
        sys.path.remove(str(service_root))
    sys.path.insert(0, str(service_root))
    for loaded_name in list(sys.modules):
        if loaded_name == "config" or loaded_name.startswith("config."):
            sys.modules.pop(loaded_name, None)
        if loaded_name == "core" or loaded_name.startswith("core."):
            sys.modules.pop(loaded_name, None)

    spec = spec_from_file_location(module_name, module_path)
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FakeTransport:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def request(self, **kwargs):
        self.calls.append(kwargs)
        return self.response


def test_bluetooth_adapter_normalizes_characteristic_write():
    module = _load_module("xuanwu_gateway_bluetooth_adapter", "bluetooth_adapter.py")
    transport = FakeTransport({"status": "ok", "value": True})
    adapter = module.BluetoothAdapter(transport=transport)

    result = adapter.dispatch(
        {
            "request_id": "req-ble-001",
            "gateway_id": "gateway-ble-001",
            "adapter_type": "bluetooth",
            "device_id": "ble-device-001",
            "capability_code": "wireless.characteristic.write",
            "command_name": "write_characteristic",
            "route": {
                "bridge_url": "http://ble-bridge.local",
                "device_address": "AA:BB:CC:DD:EE:FF",
                "service_uuid": "180F",
                "characteristic_uuid": "2A19",
            },
            "arguments": {"value": 85},
        }
    )

    assert result["status"] == "succeeded"
    assert transport.calls[0]["device_key"] == "AA:BB:CC:DD:EE:FF"
    assert transport.calls[0]["characteristic_uuid"] == "2A19"


def test_nearlink_adapter_normalizes_command_dispatch():
    module = _load_module("xuanwu_gateway_nearlink_adapter", "nearlink_adapter.py")
    transport = FakeTransport({"status": "ok", "latency_ms": 4})
    adapter = module.NearlinkAdapter(transport=transport)

    result = adapter.dispatch(
        {
            "request_id": "req-nl-001",
            "gateway_id": "gateway-nl-001",
            "adapter_type": "nearlink",
            "device_id": "nearlink-device-001",
            "capability_code": "wireless.nearlink.command",
            "command_name": "dispatch_command",
            "route": {
                "bridge_url": "http://nearlink-bridge.local",
                "link_id": "nl-link-001",
            },
            "arguments": {"mode": "burst", "power": 3},
        }
    )

    assert result["status"] == "succeeded"
    assert transport.calls[0]["device_key"] == "nl-link-001"
    assert transport.calls[0]["payload"]["mode"] == "burst"
