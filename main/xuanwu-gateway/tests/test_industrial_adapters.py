from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys


def _load_module(module_name, relative_path):
    root = Path(__file__).resolve().parents[3]
    module_path = root / "main" / "xuanwu-gateway" / "core" / "adapters" / relative_path
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


def test_modbus_tcp_adapter_normalizes_register_read():
    module = _load_module("xuanwu_gateway_modbus_adapter", "modbus_tcp_adapter.py")
    transport = FakeTransport({"status": "ok", "values": [230, 231]})
    adapter = module.ModbusTcpAdapter(transport=transport)

    result = adapter.dispatch(
        {
            "request_id": "req-modbus-001",
            "gateway_id": "gateway-modbus-001",
            "adapter_type": "modbus_tcp",
            "device_id": "plc-001",
            "capability_code": "industrial.register.read",
            "command_name": "read_holding_registers",
            "route": {
                "host": "10.0.0.20",
                "port": 502,
                "unit_id": 1,
                "address": 100,
                "quantity": 2,
            },
        }
    )

    assert result["status"] == "succeeded"
    assert transport.calls[0]["function"] == "read_holding_registers"
    assert result["result"]["protocol_response"]["values"] == [230, 231]


def test_opc_ua_adapter_normalizes_node_read():
    module = _load_module("xuanwu_gateway_opcua_adapter", "opc_ua_adapter.py")
    transport = FakeTransport({"status": "ok", "value": 42.5})
    adapter = module.OpcUaAdapter(transport=transport)

    result = adapter.dispatch(
        {
            "request_id": "req-opcua-001",
            "gateway_id": "gateway-opcua-001",
            "adapter_type": "opc_ua",
            "device_id": "opcua-station-001",
            "capability_code": "industrial.node.read",
            "command_name": "read_node",
            "route": {
                "endpoint": "opc.tcp://10.0.0.30:4840",
                "node_id": "ns=2;s=Demo.Static.Scalar.Double",
            },
        }
    )

    assert result["status"] == "succeeded"
    assert transport.calls[0]["node_id"] == "ns=2;s=Demo.Static.Scalar.Double"
    assert result["result"]["protocol_response"]["value"] == 42.5


def test_bacnet_ip_adapter_normalizes_property_read():
    module = _load_module("xuanwu_gateway_bacnet_adapter", "bacnet_ip_adapter.py")
    transport = FakeTransport({"status": "ok", "value": "active"})
    adapter = module.BacnetIpAdapter(transport=transport)

    result = adapter.dispatch(
        {
            "request_id": "req-bacnet-001",
            "gateway_id": "gateway-bacnet-001",
            "adapter_type": "bacnet_ip",
            "device_id": "ahu-001",
            "capability_code": "industrial.property.read",
            "command_name": "read_property",
            "route": {
                "address": "192.168.10.20",
                "object_type": "analogValue",
                "object_instance": 3,
                "property_name": "presentValue",
            },
        }
    )

    assert result["status"] == "succeeded"
    assert transport.calls[0]["property_name"] == "presentValue"
    assert result["result"]["protocol_response"]["value"] == "active"


def test_can_gateway_adapter_normalizes_frame_command():
    module = _load_module("xuanwu_gateway_can_adapter", "can_gateway_adapter.py")
    transport = FakeTransport({"status": "ok", "frame_id": 321, "acknowledged": True})
    adapter = module.CanGatewayAdapter(transport=transport)

    result = adapter.dispatch(
        {
            "request_id": "req-can-001",
            "gateway_id": "gateway-can-001",
            "adapter_type": "can_gateway",
            "device_id": "can-device-001",
            "capability_code": "industrial.frame.command",
            "command_name": "send_frame",
            "route": {
                "bridge_url": "http://can-bridge.local",
                "channel": "can0",
                "frame_id": 321,
                "dlc": 8,
            },
            "arguments": {"data": [1, 2, 3, 4]},
        }
    )

    assert result["status"] == "succeeded"
    assert transport.calls[0]["frame_id"] == 321
    assert result["result"]["protocol_response"]["acknowledged"] is True
