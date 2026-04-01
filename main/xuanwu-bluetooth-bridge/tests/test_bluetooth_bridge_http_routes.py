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
    app_module = _load_module(root / "main" / "xuanwu-bluetooth-bridge" / "app.py", "xuanwu_bluetooth_bridge_app")
    app = app_module.create_app({"server": {}, "bridge": {}, "gateway": {}})
    paths = sorted(route.resource.canonical for route in app.router.routes() if hasattr(route.resource, "canonical"))
    assert "/bluetooth/v1/health" in paths
    assert "/bluetooth/v1/scans:start" in paths
    assert "/bluetooth/v1/devices/{device_key}:connect" in paths
    assert "/bluetooth/v1/devices/{device_key}/characteristics:subscribe" in paths


def test_handler_supports_scan_and_characteristic_operations():
    root = Path(__file__).resolve().parents[3]
    runtime_module = _load_module(
        root / "main" / "xuanwu-bluetooth-bridge" / "core" / "runtime.py",
        "xuanwu_bluetooth_bridge_runtime",
    )
    handler_module = _load_module(
        root / "main" / "xuanwu-bluetooth-bridge" / "core" / "api" / "bridge_handler.py",
        "xuanwu_bluetooth_bridge_handler",
    )
    class Callback:
        async def post_http_push(self, payload):
            return payload

        async def post_bridge_event(self, payload):
            return payload

        async def post_command_result(self, payload):
            return payload

    callback_client = Callback()
    runtime = runtime_module.BluetoothBridgeRuntime(
        {
            "bridge": {
                "bridge_id": "bluetooth-bridge-test",
                "auth_token": "bridge-secret",
                "scan": {"default_timeout_seconds": 8, "max_concurrent_scans": 2},
                "connections": {"max_active_devices": 5},
                "demo": {"enabled": True, "device_prefix": "XW-BLE"},
            },
            "gateway": {},
        },
        callback_client=callback_client,
    )
    handler = handler_module.BluetoothBridgeHandler(
        {"bridge": {"auth_token": "bridge-secret"}, "gateway": {}},
        runtime=runtime,
        callback_client=callback_client,
    )

    scan_request = make_mocked_request(
        "POST",
        "/bluetooth/v1/scans:start",
        headers={"Authorization": "Bearer bridge-secret"},
    )
    scan_request._read_bytes = b'{"filters":{"name_prefix":"XW-BLE"}}'
    scan_response = asyncio.run(handler.handle_start_scan(scan_request))
    assert scan_response.status == 201

    device_key = next(iter(runtime.devices))
    connect_request = make_mocked_request(
        "POST",
        f"/bluetooth/v1/devices/{device_key}:connect",
        match_info={"device_key": device_key},
        headers={"Authorization": "Bearer bridge-secret"},
    )
    connect_response = asyncio.run(handler.handle_connect_device(connect_request))
    assert connect_response.status == 200

    read_request = make_mocked_request(
        "POST",
        f"/bluetooth/v1/devices/{device_key}/characteristics:read",
        match_info={"device_key": device_key},
        headers={"Authorization": "Bearer bridge-secret"},
    )
    read_request._read_bytes = b'{"service_uuid":"180f","characteristic_uuid":"2a19","encoding":"uint8"}'
    read_response = asyncio.run(handler.handle_read_characteristic(read_request))
    assert read_response.status == 200
