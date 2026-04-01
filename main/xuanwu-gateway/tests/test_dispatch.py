import asyncio
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

from aiohttp.test_utils import make_mocked_request


def _load_handler_module():
    root = Path(__file__).resolve().parents[3]
    module_path = root / "main" / "xuanwu-gateway" / "core" / "api" / "gateway_handler.py"
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


def test_dispatch_routes_command_to_matching_adapter():
    class FakeManagementClient:
        def __init__(self):
            self.discovered = []
            self.command_results = []

        async def post_device_heartbeat(self, device_id, payload):
            return False

        async def upsert_discovered_device(self, payload):
            self.discovered.append(payload)
            return payload

        async def post_command_result(self, payload):
            self.command_results.append(payload)
            return payload

    management_client = FakeManagementClient()
    handler = _load_handler_module().GatewayHandler({}, management_client=management_client)
    handler.registry.register(
        _load_handler_module().create_builtin_registry().get("http").__class__(
            transport=type(
                "FakeTransport",
                (),
                {
                    "request": lambda self, **kwargs: {
                        "status_code": 200,
                        "body": {"ok": True},
                        "headers": {},
                    }
                },
            )()
        )
    )
    request = make_mocked_request("POST", "/gateway/v1/commands:dispatch")
    request._read_bytes = (
        b'{"request_id":"req-001","gateway_id":"gateway-http-001","adapter_type":"http",'
        b'"device_id":"device-001","capability_code":"switch.on_off","command_name":"turn_on","arguments":{"state":true},'
        b'"route":{"url":"http://device.local/api/power","method":"POST","body_template":{"power":"{arguments.state}"}}}'
    )

    response = asyncio.run(handler.handle_dispatch_command(request))

    assert response.status == 200
    payload = handler._loads_json(response.text)
    assert payload["adapter_type"] == "http"
    assert payload["status"] == "succeeded"
    assert payload["result"]["command_name"] == "turn_on"
    assert management_client.discovered[0]["device_id"] == "device-001"
    assert management_client.command_results[0]["device_id"] == "device-001"


def test_dispatch_returns_404_for_unknown_adapter():
    handler = _load_handler_module().GatewayHandler({})
    request = make_mocked_request("POST", "/gateway/v1/commands:dispatch")
    request._read_bytes = (
        b'{"request_id":"req-002","gateway_id":"gateway-zigbee-001","adapter_type":"zigbee","device_id":"device-002"}'
    )

    response = asyncio.run(handler.handle_dispatch_command(request))

    assert response.status == 404
    payload = handler._loads_json(response.text)
    assert payload["error"] == "adapter_not_found"


def test_health_and_config_endpoints_return_status_and_config():
    handler = _load_handler_module().GatewayHandler({"gateway": {"site": "lab-a"}})

    health_response = asyncio.run(
        handler.handle_health(make_mocked_request("GET", "/gateway/v1/health"))
    )
    config_response = asyncio.run(
        handler.handle_get_config(make_mocked_request("GET", "/gateway/v1/config"))
    )

    assert health_response.status == 200
    assert config_response.status == 200
    assert handler._loads_json(health_response.text)["status"] == "ok"
    assert handler._loads_json(config_response.text)["gateway"]["site"] == "lab-a"


def test_commands_alias_and_device_state_work():
    class FakeManagementClient:
        async def post_device_heartbeat(self, device_id, payload):
            return True

        async def upsert_discovered_device(self, payload):
            raise AssertionError("discovery should not run when heartbeat succeeds")

        async def post_command_result(self, payload):
            return payload

    handler = _load_handler_module().GatewayHandler({}, management_client=FakeManagementClient())
    handler.registry.register(
        _load_handler_module().create_builtin_registry().get("http").__class__(
            transport=type(
                "FakeTransport",
                (),
                {
                    "request": lambda self, **kwargs: {
                        "status_code": 200,
                        "body": {"ok": True},
                        "headers": {},
                    }
                },
            )()
        )
    )
    dispatch_request = make_mocked_request("POST", "/gateway/v1/commands")
    dispatch_request._read_bytes = (
        b'{"request_id":"req-003","gateway_id":"gateway-http-001","adapter_type":"http",'
        b'"device_id":"device-003","capability_code":"switch.on_off","command_name":"turn_on","arguments":{"state":true},'
        b'"route":{"url":"http://device.local/api/power","method":"POST","body_template":{"power":"{arguments.state}"}}}'
    )

    dispatch_response = asyncio.run(handler.handle_command_collection(dispatch_request))
    state_response = asyncio.run(
        handler.handle_get_device_state(
            make_mocked_request(
                "GET",
                "/gateway/v1/devices/device-003/state",
                match_info={"device_id": "device-003"},
            )
        )
    )

    assert dispatch_response.status == 200
    assert state_response.status == 200
    assert handler._loads_json(state_response.text)["device_id"] == "device-003"


def test_job_execution_dispatches_real_gateway_command_payload():
    class FakeManagementClient:
        def __init__(self):
            self.discovered = []

        async def post_device_heartbeat(self, device_id, payload):
            return False

        async def upsert_discovered_device(self, payload):
            self.discovered.append(payload)
            return payload

        async def post_command_result(self, payload):
            return payload

    management_client = FakeManagementClient()
    handler = _load_handler_module().GatewayHandler({}, management_client=management_client)
    handler.registry.register(
        _load_handler_module().create_builtin_registry().get("http").__class__(
            transport=type(
                "FakeTransport",
                (),
                {
                    "request": lambda self, **kwargs: {
                        "status_code": 200,
                        "body": {"ok": True},
                        "headers": {},
                    }
                },
            )()
        )
    )
    request = make_mocked_request("POST", "/gateway/v1/jobs:execute")
    request._read_bytes = (
        b'{"job_run_id":"run-gateway-001","job_type":"device_command","executor_type":"gateway",'
        b'"payload":{"request_id":"req-004","gateway_id":"gateway-http-001","adapter_type":"http",'
        b'"device_id":"device-004","capability_code":"switch.on_off","command_name":"turn_off","arguments":{"state":false},'
        b'"route":{"url":"http://device.local/api/power","method":"POST","body_template":{"power":"{arguments.state}"}}}}'
    )

    response = asyncio.run(handler.handle_execute_job(request))

    assert response.status == 200
    payload = handler._loads_json(response.text)
    assert payload["status"] == "completed"
    assert payload["job_run_id"] == "run-gateway-001"
    assert payload["result"]["result"]["command_name"] == "turn_off"
    assert management_client.discovered[0]["device_id"] == "device-004"


def test_mqtt_ingest_can_use_mqtt_adapter_normalization():
    handler_module = _load_handler_module()

    class FakeMqttAdapter:
        adapter_type = "mqtt"

        def normalize_broker_message(self, payload):
            return {
                "status": "accepted",
                "telemetry": [
                    {
                        "telemetry_id": "telemetry-mqtt-001",
                        "device_id": payload["device_id"],
                        "gateway_id": payload["gateway_id"],
                        "capability_code": "sensor.mqtt",
                        "observed_at": payload["observed_at"],
                        "metrics": payload["telemetry"],
                    }
                ],
                "events": [
                    {
                        "event_id": "event-mqtt-001",
                        "device_id": payload["device_id"],
                        "gateway_id": payload["gateway_id"],
                        "event_type": "telemetry.reported",
                        "severity": "info",
                        "occurred_at": payload["observed_at"],
                        "payload": {"topic": payload["topic"], **payload["telemetry"]},
                    }
                ],
            }

    class FakeRegistry:
        def __init__(self):
            self.adapter = FakeMqttAdapter()

        def get(self, adapter_type):
            if adapter_type == "mqtt":
                return self.adapter
            return None

        def describe(self):
            return [{"adapter_type": "mqtt"}]

    class FakeManagementClient:
        def __init__(self):
            self.telemetry = []
            self.events = []
            self.discovered = []

        async def post_telemetry(self, payload):
            self.telemetry.append(payload)

        async def post_event(self, payload):
            self.events.append(payload)

        async def post_device_heartbeat(self, device_id, payload):
            return False

        async def upsert_discovered_device(self, payload):
            self.discovered.append(payload)
            return payload

    management_client = FakeManagementClient()
    handler = handler_module.GatewayHandler({}, registry=FakeRegistry(), management_client=management_client)
    request = make_mocked_request("POST", "/gateway/v1/ingest/mqtt")
    request._read_bytes = (
        b'{"adapter_type":"mqtt","device_id":"sensor-mqtt-001","gateway_id":"gateway-mqtt-001",'
        b'"topic":"factory/line-1/temp","observed_at":"2026-03-31T10:00:00Z",'
        b'"telemetry":{"temperature":24.6,"humidity":53.1}}'
    )

    response = asyncio.run(handler.handle_ingest_mqtt(request))

    assert response.status == 202
    assert management_client.telemetry[0]["metrics"]["temperature"] == 24.6
    assert management_client.events[0]["payload"]["topic"] == "factory/line-1/temp"
    assert management_client.discovered[0]["device_id"] == "sensor-mqtt-001"
