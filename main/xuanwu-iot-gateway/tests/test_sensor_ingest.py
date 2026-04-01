import asyncio
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

from aiohttp.test_utils import make_mocked_request


def _load_handler_module():
    root = Path(__file__).resolve().parents[3]
    module_path = root / "main" / "xuanwu-iot-gateway" / "core" / "api" / "gateway_handler.py"
    service_root = module_path.parents[2]

    while str(service_root) in sys.path:
        sys.path.remove(str(service_root))
    sys.path.insert(0, str(service_root))
    for module_name in list(sys.modules):
        if module_name == "config" or module_name.startswith("config."):
            sys.modules.pop(module_name, None)
        if module_name == "core" or module_name.startswith("core."):
            sys.modules.pop(module_name, None)

    spec = spec_from_file_location("xuanwu_gateway_handler", module_path)
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FakeManagementClient:
    def __init__(self):
        self.telemetry = []
        self.events = []
        self.heartbeats = []
        self.discovered = []

    async def post_telemetry(self, payload):
        self.telemetry.append(payload)
        return payload

    async def post_event(self, payload):
        self.events.append(payload)
        return payload

    async def post_device_heartbeat(self, device_id, payload):
        self.heartbeats.append((device_id, payload))
        return False

    async def upsert_discovered_device(self, payload):
        self.discovered.append(payload)
        return payload


def test_http_push_ingest_normalizes_telemetry_and_event():
    module = _load_handler_module()
    management_client = FakeManagementClient()
    handler = module.GatewayHandler({}, management_client=management_client)
    request = make_mocked_request("POST", "/gateway/v1/ingest/http-push")
    request._read_bytes = (
        b'{"adapter_type":"sensor_http_push","gateway_id":"gateway-http-push-001","device_id":"sensor-001",'
        b'"capability_code":"sensor.temperature","observed_at":"2026-03-31T10:00:00Z",'
        b'"telemetry":{"temperature_c":24.6},"event":{"event_type":"telemetry.reported","severity":"info"}}'
    )

    response = asyncio.run(handler.handle_ingest_http_push(request))

    assert response.status == 202
    payload = handler._loads_json(response.text)
    assert payload["status"] == "accepted"
    assert management_client.telemetry[0]["device_id"] == "sensor-001"
    assert management_client.telemetry[0]["metrics"]["temperature_c"] == 24.6
    assert management_client.events[0]["event_type"] == "telemetry.reported"
    assert management_client.discovered[0]["device_id"] == "sensor-001"
    assert management_client.discovered[0]["ingress_type"] == "gateway"


def test_mqtt_ingest_normalizes_telemetry_and_event():
    module = _load_handler_module()
    management_client = FakeManagementClient()
    handler = module.GatewayHandler({}, management_client=management_client)
    request = make_mocked_request("POST", "/gateway/v1/ingest/mqtt")
    request._read_bytes = (
        b'{"adapter_type":"sensor_mqtt","gateway_id":"gateway-mqtt-telemetry-001","device_id":"sensor-002",'
        b'"topic":"site/plant/sensor-002/telemetry","capability_code":"sensor.temperature","observed_at":"2026-03-31T10:01:00Z",'
        b'"telemetry":{"temperature_c":26.1}}'
    )

    response = asyncio.run(handler.handle_ingest_mqtt(request))

    assert response.status == 202
    payload = handler._loads_json(response.text)
    assert payload["status"] == "accepted"
    assert management_client.telemetry[0]["device_id"] == "sensor-002"
    assert management_client.events[0]["payload"]["topic"] == "site/plant/sensor-002/telemetry"
    assert management_client.discovered[0]["adapter_type"] == "sensor_mqtt"


def test_home_assistant_ingest_normalizes_state_change_event():
    module = _load_handler_module()
    management_client = FakeManagementClient()
    handler = module.GatewayHandler({}, management_client=management_client)
    request = make_mocked_request("POST", "/gateway/v1/ingest/home-assistant")
    request._read_bytes = (
        b'{"adapter_type":"home_assistant","gateway_id":"gateway-ha-001","device_id":"light-living-room",'
        b'"observed_at":"2026-03-31T10:03:00Z","entity_id":"light.living_room",'
        b'"state":{"state":"on","attributes":{"brightness":180,"color_mode":"rgb"}}}'
    )

    response = asyncio.run(handler.handle_ingest_home_assistant(request))

    assert response.status == 202
    payload = handler._loads_json(response.text)
    assert payload["status"] == "accepted"
    assert management_client.telemetry[0]["metrics"]["brightness"] == 180
    assert management_client.events[0]["event_type"] == "home_assistant.state_changed"
    assert management_client.discovered[0]["adapter_type"] == "home_assistant"
