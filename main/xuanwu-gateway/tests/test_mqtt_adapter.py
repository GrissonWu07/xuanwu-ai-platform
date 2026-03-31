from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys


def _load_mqtt_adapter_module():
    root = Path(__file__).resolve().parents[3]
    module_path = root / "main" / "xuanwu-gateway" / "core" / "adapters" / "mqtt_adapter.py"
    service_root = module_path.parents[2]

    while str(service_root) in sys.path:
        sys.path.remove(str(service_root))
    sys.path.insert(0, str(service_root))
    for module_name in list(sys.modules):
        if module_name == "config" or module_name.startswith("config."):
            sys.modules.pop(module_name, None)
        if module_name == "core" or module_name.startswith("core."):
            sys.modules.pop(module_name, None)

    spec = spec_from_file_location("xuanwu_gateway_mqtt_adapter", module_path)
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FakeMqttTransport:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def publish(self, **kwargs):
        self.calls.append(kwargs)
        return self.response


def test_mqtt_adapter_publishes_protocol_shaped_command():
    module = _load_mqtt_adapter_module()
    transport = FakeMqttTransport({"status": "published", "topic": "site/plant/device-100/cmd"})
    adapter = module.MqttAdapter(transport=transport)

    result = adapter.dispatch(
        {
            "request_id": "req-mqtt-001",
            "gateway_id": "gateway-mqtt-001",
            "adapter_type": "mqtt",
            "device_id": "device-100",
            "capability_code": "switch.on_off",
            "command_name": "turn_on",
            "arguments": {"state": True},
            "route": {
                "broker_host": "mqtt.internal.local",
                "broker_port": 1883,
                "topic": "site/plant/device-100/cmd",
                "qos": 1,
                "retain": False,
                "payload_template": {"power": "{arguments.state}"},
                "timeout_ms": 4000,
            },
        }
    )

    assert result["status"] == "succeeded"
    assert transport.calls[0]["broker_host"] == "mqtt.internal.local"
    assert transport.calls[0]["topic"] == "site/plant/device-100/cmd"
    assert transport.calls[0]["payload"] == {"power": True}
    assert transport.calls[0]["qos"] == 1


def test_mqtt_adapter_normalizes_publish_failure():
    module = _load_mqtt_adapter_module()
    transport = FakeMqttTransport({"status": "failed", "reason": "broker unavailable"})
    adapter = module.MqttAdapter(transport=transport)

    result = adapter.dispatch(
        {
            "request_id": "req-mqtt-002",
            "gateway_id": "gateway-mqtt-001",
            "adapter_type": "mqtt",
            "device_id": "device-100",
            "capability_code": "switch.on_off",
            "command_name": "turn_off",
            "arguments": {"state": False},
            "route": {
                "broker_host": "mqtt.internal.local",
                "topic": "site/plant/device-100/cmd",
            },
        }
    )

    assert result["status"] == "failed"
    assert result["error"]["code"] == "mqtt_publish_failed"


def test_mqtt_adapter_normalizes_broker_message_into_gateway_ingest_payload():
    module = _load_mqtt_adapter_module()
    adapter = module.MqttAdapter()

    result = adapter.normalize_broker_message(
        {
            "device_id": "sensor-mqtt-001",
            "gateway_id": "gateway-mqtt-001",
            "topic": "factory/line-1/temp",
            "observed_at": "2026-03-31T10:00:00Z",
            "telemetry": {"temperature": 24.6, "humidity": 53.1},
        }
    )

    assert result["status"] == "accepted"
    assert result["telemetry"][0]["metrics"]["temperature"] == 24.6
    assert result["events"][0]["payload"]["topic"] == "factory/line-1/temp"


def test_mqtt_adapter_ingest_uses_broker_message_normalization():
    module = _load_mqtt_adapter_module()
    adapter = module.MqttAdapter()

    result = adapter.ingest(
        {
            "device_id": "sensor-mqtt-002",
            "gateway_id": "gateway-mqtt-001",
            "topic": "factory/line-2/temp",
            "observed_at": "2026-03-31T10:05:00Z",
            "telemetry": {"temperature": 25.1},
        }
    )

    assert result["status"] == "accepted"
    assert result["telemetry"][0]["device_id"] == "sensor-mqtt-002"
    assert result["events"][0]["payload"]["topic"] == "factory/line-2/temp"
