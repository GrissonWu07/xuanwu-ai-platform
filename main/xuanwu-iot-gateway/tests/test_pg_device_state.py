from __future__ import annotations

import asyncio
import tempfile
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

from aiohttp.test_utils import make_mocked_request


def _load_gateway_module():
    root = Path(__file__).resolve().parents[3]
    module_path = root / "main" / "xuanwu-iot-gateway" / "app.py"
    service_root = module_path.parent

    while str(service_root) in sys.path:
        sys.path.remove(str(service_root))
    sys.path.insert(0, str(service_root))
    for module_name in list(sys.modules):
        if module_name == "config" or module_name.startswith("config."):
            sys.modules.pop(module_name, None)
        if module_name == "core" or module_name.startswith("core."):
            sys.modules.pop(module_name, None)

    spec = spec_from_file_location("xuanwu_iot_gateway_app", module_path)
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_gateway_state_persists_last_command() -> None:
    module = _load_gateway_module()

    class FakeManagementClient:
        async def post_device_heartbeat(self, device_id, payload):
            return True

        async def upsert_discovered_device(self, payload):
            raise AssertionError("discovery should not run when heartbeat succeeds")

        async def post_command_result(self, payload):
            return payload

    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "iot-state.db"
        app = module.create_http_app(
            {
                "server": {"host": "127.0.0.1", "http_port": 18084},
                "management": {},
                "state": {
                    "backend": "postgres",
                    "postgres": {
                        "url": f"sqlite+pysqlite:///{db_path.as_posix()}",
                        "schema": "xw_iot",
                    },
                },
            }
        )
        handler = app[module.GATEWAY_HANDLER_KEY]
        try:
            handler.management_client = FakeManagementClient()
            http_adapter_cls = handler.registry.get("http").__class__
            handler.registry.register(
                http_adapter_cls(
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
                b'{"request_id":"req-state-001","gateway_id":"gateway-http-001","adapter_type":"http",'
                b'"device_id":"device-1","capability_code":"switch.on_off","command_name":"turn_on","arguments":{"state":true},'
                b'"route":{"url":"http://device.local/api/power","method":"POST","body_template":{"power":"{arguments.state}"}}}'
            )

            response = asyncio.run(handler.handle_dispatch_command(request))
            state = handler.state_store.get_device_state("device-1")

            assert response.status == 200
            assert state["device_id"] == "device-1"
            assert state["last_command_name"] == "turn_on"
        finally:
            handler.state_store.close()
