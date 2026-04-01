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

    spec = spec_from_file_location("xuanwu_gateway_handler_bridge_callbacks", module_path)
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_bridge_event_and_command_result_callbacks_flow_into_management_surfaces():
    module = _load_handler_module()

    class FakeManagementClient:
        def __init__(self):
            self.events = []
            self.telemetry = []
            self.command_results = []
            self.discovered = []

        async def post_event(self, payload):
            self.events.append(payload)
            return payload

        async def post_telemetry(self, payload):
            self.telemetry.append(payload)
            return payload

        async def post_command_result(self, payload):
            self.command_results.append(payload)
            return payload

        async def post_device_heartbeat(self, device_id, payload):
            return False

        async def upsert_discovered_device(self, payload):
            self.discovered.append(payload)
            return payload

    management_client = FakeManagementClient()
    handler = module.GatewayHandler({}, management_client=management_client)

    event_request = make_mocked_request("POST", "/gateway/v1/bridge/events")
    event_request._read_bytes = (
        b'{"bridge_type":"bluetooth","bridge_id":"bridge-001","device_key":"AA:BB:CC:DD:EE:01",'
        b'"event_type":"bluetooth.notification","timestamp":"2026-03-31T10:20:00Z",'
        b'"telemetry":{"battery":91},"payload":{"service_uuid":"180f","characteristic_uuid":"2a19"}}'
    )
    event_response = asyncio.run(handler.handle_bridge_event(event_request))

    assert event_response.status == 202
    assert management_client.events[0]["event_type"] == "bluetooth.notification"
    assert management_client.telemetry[0]["metrics"]["battery"] == 91
    assert management_client.discovered[0]["protocol_type"] == "bluetooth"

    result_request = make_mocked_request("POST", "/gateway/v1/commands:dispatch-result")
    result_request._read_bytes = (
        b'{"request_id":"req-bridge-result-001","gateway_id":"gateway-wireless-001","adapter_type":"nearlink",'
        b'"result":{"device_id":"device-nearlink-001","command_name":"turn_on"},"status":"succeeded"}'
    )
    result_response = asyncio.run(handler.handle_command_dispatch_result(result_request))

    assert result_response.status == 202
    assert management_client.command_results[0]["adapter_type"] == "nearlink"
