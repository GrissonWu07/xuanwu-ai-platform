from aiohttp import web

from core.api.gateway_handler import GatewayHandler


def create_http_app(config: dict) -> web.Application:
    app = web.Application()
    handler = GatewayHandler(config)
    app.add_routes(
        [
            web.get("/gateway/v1/adapters", handler.handle_list_adapters),
            web.get("/gateway/v1/health", handler.handle_health),
            web.get("/gateway/v1/config", handler.handle_get_config),
            web.post("/gateway/v1/commands", handler.handle_command_collection),
            web.post("/gateway/v1/commands:dispatch", handler.handle_dispatch_command),
            web.get("/gateway/v1/devices/{device_id}/state", handler.handle_get_device_state),
        ]
    )
    return app
