from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import types
import json


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


def test_modbus_tcp_adapter_reads_coils():
    module = _load_module("xuanwu_gateway_modbus_adapter_coils", "modbus_tcp_adapter.py")
    transport = FakeTransport({"status": "ok", "values": [True, False, True]})
    adapter = module.ModbusTcpAdapter(transport=transport)

    result = adapter.dispatch(
        {
            "request_id": "req-modbus-coils-001",
            "gateway_id": "gateway-modbus-001",
            "adapter_type": "modbus_tcp",
            "device_id": "plc-001",
            "capability_code": "industrial.coil.read",
            "command_name": "read_coils",
            "route": {
                "host": "10.0.0.20",
                "address": 1,
                "quantity": 3,
            },
        }
    )

    assert result["status"] == "succeeded"
    assert transport.calls[0]["function"] == "read_coils"
    assert result["result"]["protocol_response"]["values"] == [True, False, True]


def test_modbus_tcp_adapter_reads_discrete_inputs():
    module = _load_module("xuanwu_gateway_modbus_adapter_inputs", "modbus_tcp_adapter.py")
    transport = FakeTransport({"status": "ok", "values": [False, True]})
    adapter = module.ModbusTcpAdapter(transport=transport)

    result = adapter.dispatch(
        {
            "request_id": "req-modbus-discrete-001",
            "gateway_id": "gateway-modbus-001",
            "adapter_type": "modbus_tcp",
            "device_id": "plc-001",
            "capability_code": "industrial.discrete_input.read",
            "command_name": "read_discrete_inputs",
            "route": {
                "host": "10.0.0.20",
                "address": 11,
                "quantity": 2,
            },
        }
    )

    assert result["status"] == "succeeded"
    assert transport.calls[0]["function"] == "read_discrete_inputs"
    assert result["result"]["protocol_response"]["values"] == [False, True]


def test_modbus_tcp_adapter_reads_input_registers():
    module = _load_module("xuanwu_gateway_modbus_adapter_input_registers", "modbus_tcp_adapter.py")
    transport = FakeTransport({"status": "ok", "values": [11, 12, 13]})
    adapter = module.ModbusTcpAdapter(transport=transport)

    result = adapter.dispatch(
        {
            "request_id": "req-modbus-input-reg-001",
            "gateway_id": "gateway-modbus-001",
            "adapter_type": "modbus_tcp",
            "device_id": "plc-001",
            "capability_code": "industrial.input_register.read",
            "command_name": "read_input_registers",
            "route": {
                "host": "10.0.0.20",
                "address": 200,
                "quantity": 3,
            },
        }
    )

    assert result["status"] == "succeeded"
    assert transport.calls[0]["function"] == "read_input_registers"
    assert result["result"]["protocol_response"]["values"] == [11, 12, 13]


def test_pymodbus_transport_supports_read_coils(monkeypatch):
    module = _load_module("xuanwu_gateway_modbus_transport_coils", "modbus_tcp_adapter.py")

    class FakeResponse:
        def __init__(self):
            self.bits = [True, False, True, False]

        def isError(self):
            return False

    class FakeClient:
        def __init__(self, host, port, timeout):
            self.host = host
            self.port = port
            self.timeout = timeout

        def connect(self):
            return True

        def read_coils(self, address, count, slave):
            return FakeResponse()

        def close(self):
            return None

    fake_client_module = types.ModuleType("pymodbus.client")
    fake_client_module.ModbusTcpClient = FakeClient
    monkeypatch.setitem(sys.modules, "pymodbus.client", fake_client_module)

    transport = module.PymodbusTransport()
    result = transport.request(
        function="read_coils",
        host="10.0.0.20",
        port=502,
        unit_id=1,
        address=1,
        quantity=3,
        value=None,
        timeout_ms=1000,
    )

    assert result == {"status": "ok", "values": [True, False, True]}


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


def test_opc_ua_adapter_normalizes_node_browse():
    module = _load_module("xuanwu_gateway_opcua_adapter_browse", "opc_ua_adapter.py")
    transport = FakeTransport({"status": "ok", "children": ["ns=2;s=Demo.Child.1", "ns=2;s=Demo.Child.2"]})
    adapter = module.OpcUaAdapter(transport=transport)

    result = adapter.dispatch(
        {
            "request_id": "req-opcua-browse-001",
            "gateway_id": "gateway-opcua-001",
            "adapter_type": "opc_ua",
            "device_id": "opcua-station-001",
            "capability_code": "industrial.node.browse",
            "command_name": "browse_node",
            "route": {
                "endpoint": "opc.tcp://10.0.0.30:4840",
                "node_id": "ns=2;s=Demo.Root",
            },
        }
    )

    assert result["status"] == "succeeded"
    assert transport.calls[0]["action"] == "browse_node"
    assert result["result"]["protocol_response"]["children"] == ["ns=2;s=Demo.Child.1", "ns=2;s=Demo.Child.2"]


def test_opc_ua_transport_supports_browse_node(monkeypatch):
    module = _load_module("xuanwu_gateway_opcua_transport_browse", "opc_ua_adapter.py")

    class FakeNodeId:
        def __init__(self, value):
            self.value = value

        def to_string(self):
            return self.value

    class FakeChildNode:
        def __init__(self, value):
            self.nodeid = FakeNodeId(value)

    class FakeNode:
        def get_children(self):
            return [FakeChildNode("ns=2;s=Demo.Child.1"), FakeChildNode("ns=2;s=Demo.Child.2")]

    class FakeClient:
        def __init__(self, endpoint, timeout):
            self.endpoint = endpoint
            self.timeout = timeout

        def connect(self):
            return None

        def get_node(self, node_id):
            return FakeNode()

        def disconnect(self):
            return None

    fake_opcua_module = types.ModuleType("opcua")
    fake_opcua_module.Client = FakeClient
    monkeypatch.setitem(sys.modules, "opcua", fake_opcua_module)

    transport = module.OpcUaTransport()
    result = transport.request(
        action="browse_node",
        endpoint="opc.tcp://10.0.0.30:4840",
        node_id="ns=2;s=Demo.Root",
        value=None,
        timeout_ms=1000,
    )

    assert result == {"status": "ok", "children": ["ns=2;s=Demo.Child.1", "ns=2;s=Demo.Child.2"]}


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


def test_bacnet_ip_adapter_normalizes_property_multiple_read():
    module = _load_module("xuanwu_gateway_bacnet_adapter_multi", "bacnet_ip_adapter.py")
    transport = FakeTransport({"status": "ok", "values": {"presentValue": 23.1, "units": "celsius"}})
    adapter = module.BacnetIpAdapter(transport=transport)

    result = adapter.dispatch(
        {
            "request_id": "req-bacnet-multi-001",
            "gateway_id": "gateway-bacnet-001",
            "adapter_type": "bacnet_ip",
            "device_id": "ahu-001",
            "capability_code": "industrial.property.read_multiple",
            "command_name": "read_property_multiple",
            "route": {
                "address": "192.168.10.20",
                "object_type": "analogValue",
                "object_instance": 3,
                "property_names": ["presentValue", "units"],
            },
        }
    )

    assert result["status"] == "succeeded"
    assert transport.calls[0]["property_names"] == ["presentValue", "units"]
    assert result["result"]["protocol_response"]["values"]["presentValue"] == 23.1


def test_bacnet_transport_supports_property_multiple_read(monkeypatch):
    module = _load_module("xuanwu_gateway_bacnet_transport_multi", "bacnet_ip_adapter.py")

    class FakeBacnetRuntime:
        def read(self, target):
            if target.endswith("presentValue"):
                return 23.1
            if target.endswith("units"):
                return "celsius"
            raise AssertionError(f"unexpected target {target}")

        def disconnect(self):
            return None

    fake_bac0_module = types.ModuleType("BAC0")
    fake_bac0_module.lite = lambda: FakeBacnetRuntime()
    monkeypatch.setitem(sys.modules, "BAC0", fake_bac0_module)

    transport = module.BacnetTransport()
    result = transport.request(
        action="read_property_multiple",
        address="192.168.10.20",
        object_type="analogValue",
        object_instance=3,
        property_name="",
        property_names=["presentValue", "units"],
        value=None,
        timeout_ms=1000,
    )

    assert result == {"status": "ok", "values": {"presentValue": 23.1, "units": "celsius"}}


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


def test_can_gateway_adapter_normalizes_frame_query():
    module = _load_module("xuanwu_gateway_can_query_adapter", "can_gateway_adapter.py")
    transport = FakeTransport({"status": "ok", "frame_id": 322, "signals": {"motor_speed": 1450}})
    adapter = module.CanGatewayAdapter(transport=transport)

    result = adapter.dispatch(
        {
            "request_id": "req-can-query-001",
            "gateway_id": "gateway-can-001",
            "adapter_type": "can_gateway",
            "device_id": "can-device-001",
            "capability_code": "industrial.frame.query",
            "command_name": "query_frame_state",
            "route": {
                "bridge_url": "http://can-bridge.local",
                "channel": "can0",
                "frame_id": 322,
                "dlc": 8,
            },
            "arguments": {"data": [0, 0, 0, 0]},
        }
    )

    assert result["status"] == "succeeded"
    assert transport.calls[0]["frame_id"] == 322
    assert result["result"]["protocol_response"]["signals"]["motor_speed"] == 1450


def test_can_http_bridge_transport_supports_frame_query(monkeypatch):
    module = _load_module("xuanwu_gateway_can_transport_query", "can_gateway_adapter.py")

    captured = {}

    class FakeResponse:
        status = 200

        def read(self):
            return json.dumps({"signals": {"motor_speed": 1450}}).encode("utf-8")

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def fake_urlopen(req, timeout):
        captured["url"] = req.full_url
        captured["method"] = req.get_method()
        captured["body"] = json.loads(req.data.decode("utf-8"))
        return FakeResponse()

    monkeypatch.setattr(module.urllib_request, "urlopen", fake_urlopen)

    transport = module.CanHttpBridgeTransport()
    result = transport.request(
        bridge_url="http://can-bridge.local",
        channel="can0",
        frame_id=322,
        dlc=8,
        data=[0, 0, 0, 0],
        action="query_frame_state",
        timeout_ms=1000,
    )

    assert captured["url"] == "http://can-bridge.local/frames/query"
    assert captured["method"] == "POST"
    assert result["status"] == "ok"
    assert result["body"]["signals"]["motor_speed"] == 1450
