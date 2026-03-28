from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys


SERVICE_ROOT = Path(__file__).resolve().parents[1]

if str(SERVICE_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVICE_ROOT))

from core.clients.xuanwu_client import XuanWuClient
from core.api.xuanwu_proxy_handler import XuanWuProxyHandler
from aiohttp import web
from aiohttp.test_utils import make_mocked_request
import asyncio


def _load_management_app_module():
    root = Path(__file__).resolve().parents[3]
    app_path = root / "main" / "xuanwu-management-server" / "app.py"
    service_root = app_path.parent

    while str(service_root) in sys.path:
        sys.path.remove(str(service_root))
    sys.path.insert(0, str(service_root))
    for module_name in list(sys.modules):
        if module_name == "config" or module_name.startswith("config."):
            sys.modules.pop(module_name, None)
        if module_name == "core" or module_name.startswith("core."):
            sys.modules.pop(module_name, None)

    spec = spec_from_file_location("xuanwu_management_server_app", app_path)
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_xuanwu_client_builds_required_headers():
    client = XuanWuClient(
        {
            "xuanwu": {
                "base_url": "http://xuanwu.internal",
                "control_plane_secret": "cp-secret-001",
            }
        }
    )

    headers = client.build_headers("req-20260328-001")

    assert headers["X-Xiaozhi-Control-Plane-Secret"] == "cp-secret-001"
    assert headers["X-Request-Id"] == "req-20260328-001"


def test_create_app_registers_xuanwu_proxy_routes():
    module = _load_management_app_module()

    app = module.create_app(
        {
            "server": {"auth_key": "runtime-secret"},
            "control-plane": {},
            "xuanwu": {
                "base_url": "http://xuanwu.internal",
                "control_plane_secret": "cp-secret-001",
            },
        }
    )
    registered_paths = sorted(
        route.resource.canonical for route in app.router.routes() if hasattr(route.resource, "canonical")
    )

    assert "/control-plane/v1/xuanwu/agents" in registered_paths
    assert "/control-plane/v1/xuanwu/model-providers" in registered_paths
    assert "/control-plane/v1/xuanwu/models" in registered_paths


def test_proxy_handler_returns_upstream_agent_payload():
    handler = XuanWuProxyHandler(
        {
            "xuanwu": {
                "base_url": "http://xuanwu.internal",
                "control_plane_secret": "cp-secret-001",
            }
        }
    )

    class FakeClient:
        async def list_agents(self, request_id: str):
            assert request_id == "req-20260328-agents"
            return 200, {"ok": True, "data": {"items": [{"id": "agent-default"}]}}

    handler.client = FakeClient()
    request = make_mocked_request(
        "GET",
        "/control-plane/v1/xuanwu/agents",
        headers={"X-Request-Id": "req-20260328-agents"},
    )

    response = asyncio.run(handler.handle_agents(request))

    assert response.status == 200
    assert response.text == '{"ok":true,"data":{"items":[{"id":"agent-default"}]}}'


def test_proxy_handler_preserves_upstream_model_error_status():
    handler = XuanWuProxyHandler(
        {
            "xuanwu": {
                "base_url": "http://xuanwu.internal",
                "control_plane_secret": "cp-secret-001",
            }
        }
    )

    class FakeClient:
        async def list_models(self, request_id: str):
            assert request_id == "req-20260328-models"
            return 401, {"ok": False, "error": {"code": "upstream_unauthorized"}}

    handler.client = FakeClient()
    request = make_mocked_request(
        "GET",
        "/control-plane/v1/xuanwu/models",
        headers={"X-Request-Id": "req-20260328-models"},
    )

    response = asyncio.run(handler.handle_models(request))

    assert response.status == 401
    assert response.text == '{"ok":false,"error":{"code":"upstream_unauthorized"}}'


def test_xuanwu_client_calls_configured_agent_endpoint():
    async def scenario():
        received: dict[str, str] = {}

        async def handle_agents(request: web.Request):
            received["path"] = request.path
            received["secret"] = request.headers.get("X-Xiaozhi-Control-Plane-Secret", "")
            received["request_id"] = request.headers.get("X-Request-Id", "")
            return web.json_response({"ok": True, "data": {"items": [{"id": "agent-main"}]}})

        upstream = web.Application()
        upstream.router.add_get("/xuanwu/v1/admin/agents", handle_agents)

        runner = web.AppRunner(upstream)
        await runner.setup()
        site = web.TCPSite(runner, "127.0.0.1", 0)
        await site.start()
        sockets = site._server.sockets
        assert sockets
        port = sockets[0].getsockname()[1]

        client = XuanWuClient(
            {
                "xuanwu": {
                    "base_url": f"http://127.0.0.1:{port}/",
                    "control_plane_secret": "cp-secret-live",
                }
            }
        )
        status, payload = await client.list_agents("req-live-agents")

        await runner.cleanup()

        assert status == 200
        assert payload == {"ok": True, "data": {"items": [{"id": "agent-main"}]}}
        assert received == {
            "path": "/xuanwu/v1/admin/agents",
            "secret": "cp-secret-live",
            "request_id": "req-live-agents",
        }

    asyncio.run(scenario())
