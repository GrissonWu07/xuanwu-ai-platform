import asyncio

from aiohttp import web

from config.logger import setup_logging
from core.api.ota_handler import OTAHandler
from core.api.runtime_handler import RuntimeHandler
from core.api.vision_handler import VisionHandler

TAG = __name__


class SimpleHttpServer:
    def __init__(self, config: dict):
        self.config = config
        self.logger = setup_logging()
        self.ota_handler = OTAHandler(config)
        self.vision_handler = VisionHandler(config)
        self.runtime_handler = RuntimeHandler(config)

    def _get_websocket_url(self, local_ip: str, port: int) -> str:
        server_config = self.config["server"]
        websocket_config = server_config.get("websocket")

        if websocket_config and "浣?" not in websocket_config:
            return websocket_config
        return f"ws://{local_ip}:{port}/xuanwu/v1/"

    async def start(self):
        try:
            server_config = self.config["server"]
            host = server_config.get("ip", "0.0.0.0")
            port = int(server_config.get("http_port", 8003))

            if port:
                app = web.Application()
                app.add_routes(
                    [
                        web.get("/xuanwu/ota/", self.ota_handler.handle_get),
                        web.post("/xuanwu/ota/", self.ota_handler.handle_post),
                        web.options("/xuanwu/ota/", self.ota_handler.handle_options),
                        web.get(
                            "/xuanwu/ota/download/{filename}",
                            self.ota_handler.handle_download,
                        ),
                        web.options(
                            "/xuanwu/ota/download/{filename}",
                            self.ota_handler.handle_options,
                        ),
                        web.get(
                            "/runtime/v1/sessions/{runtime_session_id}/context",
                            self.runtime_handler.handle_context,
                        ),
                        web.post(
                            "/runtime/v1/sessions/{runtime_session_id}/tool-executions",
                            self.runtime_handler.handle_tool_execution,
                        ),
                        web.post(
                            "/runtime/v1/sessions/{runtime_session_id}/interrupt",
                            self.runtime_handler.handle_interrupt,
                        ),
                        web.post(
                            "/runtime/v1/sessions/{runtime_session_id}/speak",
                            self.runtime_handler.handle_speak,
                        ),
                        web.options(
                            "/runtime/v1/sessions/{runtime_session_id}/context",
                            self.runtime_handler.handle_options,
                        ),
                        web.options(
                            "/runtime/v1/sessions/{runtime_session_id}/tool-executions",
                            self.runtime_handler.handle_options,
                        ),
                        web.options(
                            "/runtime/v1/sessions/{runtime_session_id}/interrupt",
                            self.runtime_handler.handle_options,
                        ),
                        web.options(
                            "/runtime/v1/sessions/{runtime_session_id}/speak",
                            self.runtime_handler.handle_options,
                        ),
                        web.get("/mcp/vision/explain", self.vision_handler.handle_get),
                        web.post("/mcp/vision/explain", self.vision_handler.handle_post),
                        web.options(
                            "/mcp/vision/explain",
                            self.vision_handler.handle_options,
                        ),
                    ]
                )

                runner = web.AppRunner(app)
                await runner.setup()
                site = web.TCPSite(runner, host, port)
                await site.start()

                while True:
                    await asyncio.sleep(3600)
        except Exception as e:
            self.logger.bind(tag=TAG).error(f"HTTP服务启动失败: {e}")
            import traceback

            self.logger.bind(tag=TAG).error(f"错误堆栈: {traceback.format_exc()}")
            raise
