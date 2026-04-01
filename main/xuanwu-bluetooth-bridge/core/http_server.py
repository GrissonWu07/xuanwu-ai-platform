from aiohttp import web

from core.api.bridge_handler import BluetoothBridgeHandler


def create_http_app(config: dict) -> web.Application:
    app = web.Application()
    handler = BluetoothBridgeHandler(config)
    app.add_routes(
        [
            web.get("/bluetooth/v1/health", handler.handle_health),
            web.get("/bluetooth/v1/adapters", handler.handle_list_adapters),
            web.post("/bluetooth/v1/scans:start", handler.handle_start_scan),
            web.post("/bluetooth/v1/scans/{scan_id}:stop", handler.handle_stop_scan),
            web.get("/bluetooth/v1/scans/{scan_id}", handler.handle_get_scan),
            web.get("/bluetooth/v1/devices", handler.handle_list_devices),
            web.get("/bluetooth/v1/devices/{device_key}", handler.handle_get_device),
            web.post("/bluetooth/v1/devices/{device_key}:connect", handler.handle_connect_device),
            web.post("/bluetooth/v1/devices/{device_key}:disconnect", handler.handle_disconnect_device),
            web.post("/bluetooth/v1/devices/{device_key}/characteristics:read", handler.handle_read_characteristic),
            web.post("/bluetooth/v1/devices/{device_key}/characteristics:write", handler.handle_write_characteristic),
            web.post(
                "/bluetooth/v1/devices/{device_key}/characteristics:subscribe",
                handler.handle_subscribe_characteristic,
            ),
            web.post(
                "/bluetooth/v1/devices/{device_key}/characteristics:unsubscribe",
                handler.handle_unsubscribe_characteristic,
            ),
        ]
    )
    return app
