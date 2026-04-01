from aiohttp import web

from core.api.bridge_handler import NearlinkBridgeHandler


def create_http_app(config: dict) -> web.Application:
    app = web.Application()
    handler = NearlinkBridgeHandler(config)
    app.add_routes(
        [
            web.get("/nearlink/v1/health", handler.handle_health),
            web.get("/nearlink/v1/adapters", handler.handle_list_adapters),
            web.post("/nearlink/v1/discovery:start", handler.handle_start_discovery),
            web.post("/nearlink/v1/discovery/{discovery_id}:stop", handler.handle_stop_discovery),
            web.get("/nearlink/v1/discovery/{discovery_id}", handler.handle_get_discovery),
            web.get("/nearlink/v1/devices", handler.handle_list_devices),
            web.get("/nearlink/v1/devices/{device_key}", handler.handle_get_device),
            web.post("/nearlink/v1/devices/{device_key}:connect", handler.handle_connect_device),
            web.post("/nearlink/v1/devices/{device_key}:disconnect", handler.handle_disconnect_device),
            web.post("/nearlink/v1/devices/{device_key}:command", handler.handle_command_device),
            web.post("/nearlink/v1/devices/{device_key}:query-state", handler.handle_query_state),
        ]
    )
    return app
