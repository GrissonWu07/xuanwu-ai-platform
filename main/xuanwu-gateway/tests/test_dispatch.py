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
    handler = _load_handler_module().GatewayHandler({})
    request = make_mocked_request("POST", "/gateway/v1/commands:dispatch")
    request._read_bytes = (
        b'{"request_id":"req-001","gateway_id":"gateway-http-001","adapter_type":"http",'
        b'"device_id":"device-001","capability_code":"switch.on_off","command_name":"turn_on","arguments":{"state":true}}'
    )

    response = asyncio.run(handler.handle_dispatch_command(request))

    assert response.status == 200
    payload = handler._loads_json(response.text)
    assert payload["adapter_type"] == "http"
    assert payload["status"] == "accepted"
    assert payload["result"]["command_name"] == "turn_on"


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
    handler = _load_handler_module().GatewayHandler({})
    dispatch_request = make_mocked_request("POST", "/gateway/v1/commands")
    dispatch_request._read_bytes = (
        b'{"request_id":"req-003","gateway_id":"gateway-http-001","adapter_type":"http",'
        b'"device_id":"device-003","capability_code":"switch.on_off","command_name":"turn_on","arguments":{"state":true}}'
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
    handler = _load_handler_module().GatewayHandler({})
    request = make_mocked_request("POST", "/gateway/v1/jobs:execute")
    request._read_bytes = (
        b'{"job_run_id":"run-gateway-001","job_type":"device_command","executor_type":"gateway",'
        b'"payload":{"request_id":"req-004","gateway_id":"gateway-http-001","adapter_type":"http",'
        b'"device_id":"device-004","capability_code":"switch.on_off","command_name":"turn_off","arguments":{"state":false}}}'
    )

    response = asyncio.run(handler.handle_execute_job(request))

    assert response.status == 200
    payload = handler._loads_json(response.text)
    assert payload["status"] == "completed"
    assert payload["job_run_id"] == "run-gateway-001"
    assert payload["result"]["result"]["command_name"] == "turn_off"
