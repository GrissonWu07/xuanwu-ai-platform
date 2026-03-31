from aiohttp import web

from core.api.jobs_handler import JobsHandler


def create_http_app(config: dict) -> web.Application:
    app = web.Application()
    handler = JobsHandler(config)
    app.add_routes(
        [
            web.get("/jobs/v1/health", handler.handle_health),
            web.get("/jobs/v1/config", handler.handle_get_config),
        ]
    )
    return app
