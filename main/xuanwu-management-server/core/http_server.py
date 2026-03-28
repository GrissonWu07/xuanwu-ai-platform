from aiohttp import web

from core.api.control_plane_handler import ControlPlaneHandler
from core.api.xuanwu_proxy_handler import XuanWuProxyHandler

CONFIG_KEY = web.AppKey("config", dict)


def create_http_app(config: dict) -> web.Application:
    app = web.Application()
    app[CONFIG_KEY] = config
    control_plane_handler = ControlPlaneHandler(config)
    xuanwu_proxy_handler = XuanWuProxyHandler(config)
    app.add_routes(
        [
            web.get(
                "/control-plane/v1/config/server",
                control_plane_handler.handle_get_server_config,
            ),
            web.put(
                "/control-plane/v1/config/server",
                control_plane_handler.handle_put_server_config,
            ),
            web.options(
                "/control-plane/v1/config/server",
                control_plane_handler.handle_options,
            ),
            web.get(
                "/control-plane/v1/devices/{device_id}",
                control_plane_handler.handle_get_device,
            ),
            web.put(
                "/control-plane/v1/devices/{device_id}",
                control_plane_handler.handle_put_device,
            ),
            web.options(
                "/control-plane/v1/devices/{device_id}",
                control_plane_handler.handle_options,
            ),
            web.get(
                "/control-plane/v1/agents/{agent_id}",
                control_plane_handler.handle_get_agent,
            ),
            web.put(
                "/control-plane/v1/agents/{agent_id}",
                control_plane_handler.handle_put_agent,
            ),
            web.options(
                "/control-plane/v1/agents/{agent_id}",
                control_plane_handler.handle_options,
            ),
            web.post(
                "/control-plane/v1/runtime/device-config:resolve",
                control_plane_handler.handle_resolve_device_config,
            ),
            web.options(
                "/control-plane/v1/runtime/device-config:resolve",
                control_plane_handler.handle_options,
            ),
            web.get(
                "/control-plane/v1/xuanwu/agents",
                xuanwu_proxy_handler.handle_agents,
            ),
            web.get(
                "/control-plane/v1/xuanwu/model-providers",
                xuanwu_proxy_handler.handle_model_providers,
            ),
            web.get(
                "/control-plane/v1/xuanwu/models",
                xuanwu_proxy_handler.handle_models,
            ),
        ]
    )
    return app
