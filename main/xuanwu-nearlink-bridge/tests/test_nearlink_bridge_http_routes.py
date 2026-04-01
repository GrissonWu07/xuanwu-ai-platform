import asyncio
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

from aiohttp.test_utils import make_mocked_request


def _load_module(module_path: Path, module_name: str):
    service_root = module_path.parents[1]
    while str(service_root) in sys.path:
        sys.path.remove(str(service_root))
    sys.path.insert(0, str(service_root))
    for name in list(sys.modules):
        if name == "config" or name.startswith("config."):
            sys.modules.pop(name, None)
        if name == "core" or name.startswith("core."):
            sys.modules.pop(name, None)
    spec = spec_from_file_location(module_name, module_path)
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_http_server_registers_spec_routes():
    root = Path(__file__).resolve().parents[3]
    app_module = _load_module(
        root / "main" / "xuanwu-nearlink-bridge" / "app.py",
        "xuanwu_nearlink_bridge_app",
    )
    app = app_module.create_app({"server": {}, "bridge": {}, "gateway": {}})
    paths = sorted(route.resource.canonical for route in app.router.routes() if hasattr(route.resource, "canonical"))
    assert "/nearlink/v1/health" in paths
    assert "/nearlink/v1/discovery:start" in paths
    assert "/nearlink/v1/devices/{device_key}:command" in paths
    assert "/nearlink/v1/devices/{device_key}:query-state" in paths


def test_handler_supports_discovery_and_command_operations():
    root = Path(__file__).resolve().parents[3]
    runtime_module = _load_module(
        root / "main" / "xuanwu-nearlink-bridge" / "core" / "runtime.py",
        "xuanwu_nearlink_bridge_runtime",
    )
    handler_module = _load_module(
        root / "main" / "xuanwu-nearlink-bridge" / "core" / "api" / "bridge_handler.py",
        "xuanwu_nearlink_bridge_handler",
    )

    class Callback:
        async def post_http_push(self, payload):
            return payload

        async def post_bridge_event(self, payload):
            return payload

        async def post_command_result(self, payload):
            return payload

    callback_client = Callback()
    runtime = runtime_module.NearlinkBridgeRuntime(
        {
            "bridge": {
                "bridge_id": "nearlink-bridge-test",
                "auth_token": "bridge-secret",
                "discovery": {"default_timeout_seconds": 5},
                "sessions": {"max_active_devices": 5},
                "demo": {"enabled": True, "device_prefix": "XW-NL"},
            },
            "gateway": {},
        },
        callback_client=callback_client,
    )
    handler = handler_module.NearlinkBridgeHandler(
        {"bridge": {"auth_token": "bridge-secret"}, "gateway": {}},
        runtime=runtime,
        callback_client=callback_client,
    )

    discovery_request = make_mocked_request(
        "POST",
        "/nearlink/v1/discovery:start",
        headers={"Authorization": "Bearer bridge-secret"},
    )
    discovery_request._read_bytes = b'{"filters":{"name_prefix":"XW-NL"}}'
    discovery_response = asyncio.run(handler.handle_start_discovery(discovery_request))
    assert discovery_response.status == 201

    device_key = next(iter(runtime.devices))
    connect_request = make_mocked_request(
        "POST",
        f"/nearlink/v1/devices/{device_key}:connect",
        match_info={"device_key": device_key},
        headers={"Authorization": "Bearer bridge-secret"},
    )
    connect_response = asyncio.run(handler.handle_connect_device(connect_request))
    assert connect_response.status == 200

    command_request = make_mocked_request(
        "POST",
        f"/nearlink/v1/devices/{device_key}:command",
        match_info={"device_key": device_key},
        headers={"Authorization": "Bearer bridge-secret"},
    )
    command_request._read_bytes = b'{"capability_code":"switch.on_off","action":"turn_on","arguments":{"target_state":"active"}}'
    command_response = asyncio.run(handler.handle_command_device(command_request))
    assert command_response.status == 200
