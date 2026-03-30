import asyncio
import sys
import tempfile
from pathlib import Path

from aiohttp import web


SERVICE_ROOT = Path(__file__).resolve().parents[1]
if str(SERVICE_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVICE_ROOT))
for module_name in list(sys.modules):
    if module_name == "config" or module_name.startswith("config."):
        sys.modules.pop(module_name, None)
    if module_name == "core" or module_name.startswith("core."):
        sys.modules.pop(module_name, None)

from config.xuanwu_management_client import (
    _client_kwargs,
    _management_config,
    fetch_server_config,
    generate_chat_summary,
    report_chat_history,
    resolve_private_config,
)
from core.runtime_config_exceptions import DeviceBindException, DeviceNotFoundException


def test_management_config_requires_url_and_secret():
    try:
        _management_config({"xuanwu-management-server": {"secret": "s"}})
    except ValueError as exc:
        assert str(exc) == "xuanwu-management-server url missing"
    else:
        raise AssertionError("expected url missing error")

    try:
        _management_config({"xuanwu-management-server": {"url": "http://127.0.0.1:1"}})
    except ValueError as exc:
        assert str(exc) == "xuanwu-management-server secret missing"
    else:
        raise AssertionError("expected secret missing error")


def test_client_kwargs_normalize_url_timeout_and_headers():
    kwargs = _client_kwargs(
        {
            "xuanwu-management-server": {
                "url": "http://127.0.0.1:18082/",
                "secret": "secret-001",
                "timeout": 3,
            }
        }
    )

    assert kwargs["base_url"] == "http://127.0.0.1:18082"
    assert kwargs["timeout"] == 3.0
    assert kwargs["headers"]["X-Xuanwu-Control-Secret"] == "secret-001"
    assert kwargs["headers"]["Accept"] == "application/json"


def test_management_client_round_trips_and_maps_runtime_errors():
    async def scenario():
        async def handle_server(request: web.Request):
            return web.json_response({"server": {"runtime_secret": "runtime-secret"}})

        async def handle_resolve(request: web.Request):
            payload = await request.json()
            if payload["device_id"] == "missing-device":
                return web.json_response({"error": "device_not_found"}, status=404)
            if payload["device_id"] == "bind-pending-device":
                return web.json_response({"bind_code": "654321"}, status=409)
            return web.json_response(
                {
                    "resolved_config": {
                        "prompt": "remote prompt",
                        "selected_module": payload["selected_module"],
                    }
                }
            )

        async def handle_history(request: web.Request):
            payload = await request.json()
            return web.json_response({"accepted": True, "session_id": payload["session_id"]})

        async def handle_summary(request: web.Request):
            return web.json_response({"summary_id": request.match_info["summary_id"], "status": "queued"})

        app = web.Application()
        app.router.add_get("/control-plane/v1/config/server", handle_server)
        app.router.add_post("/control-plane/v1/runtime/device-config:resolve", handle_resolve)
        app.router.add_post("/control-plane/v1/chat-history/report", handle_history)
        app.router.add_post("/control-plane/v1/chat-summaries/{summary_id}:generate", handle_summary)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "127.0.0.1", 0)
        await site.start()
        port = site._server.sockets[0].getsockname()[1]

        config = {
            "xuanwu-management-server": {
                "enabled": True,
                "url": f"http://127.0.0.1:{port}",
                "secret": "mgmt-secret",
            }
        }

        server_config = await fetch_server_config(config)
        resolved = await resolve_private_config(
            config,
            "device-001",
            "client-001",
            {"LLM": "RemoteLLM"},
        )
        history = await report_chat_history(config, {"session_id": "sess-001"})
        summary = await generate_chat_summary(config, "sess-001", {"reason": "rollup"})

        assert server_config["server"]["runtime_secret"] == "runtime-secret"
        assert resolved["prompt"] == "remote prompt"
        assert history["accepted"] is True
        assert summary["status"] == "queued"

        try:
            await resolve_private_config(config, "missing-device", "client-001", {})
        except DeviceNotFoundException as exc:
            assert str(exc) == "missing-device"
        else:
            raise AssertionError("expected DeviceNotFoundException")

        try:
            await resolve_private_config(config, "bind-pending-device", "client-001", {})
        except DeviceBindException as exc:
            assert exc.bind_code == "654321"
        else:
            raise AssertionError("expected DeviceBindException")

        await runner.cleanup()

    asyncio.run(scenario())
