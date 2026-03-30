from aiohttp import web

from core.api.gateway_handler import GatewayHandler


def create_http_app(config: dict) -> web.Application:
    app = web.Application()
    handler = GatewayHandler(config)
    app.add_routes(
        [
            web.get("/gateway/v1/adapters", handler.handle_list_adapters),
            web.post("/gateway/v1/commands:dispatch", handler.handle_dispatch_command),
        ]
    )
    return app

