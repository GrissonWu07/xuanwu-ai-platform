import json

from aiohttp import web


class JobsHandler:
    def __init__(self, config: dict):
        self.config = config

    def _json_response(self, payload: dict, *, status: int = 200) -> web.Response:
        return web.Response(
            text=json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
            content_type="application/json",
            status=status,
        )

    async def handle_health(self, request: web.Request) -> web.Response:
        return self._json_response({"status": "ok", "service": "xuanwu-jobs"})

    async def handle_get_config(self, request: web.Request) -> web.Response:
        jobs_config = self.config.get("jobs", {})
        return self._json_response(
            {
                "jobs": {
                    "queue_names": jobs_config.get("queue_names", {}),
                    "schedule_batch_size": jobs_config.get("schedule_batch_size"),
                    "poll_interval_seconds": jobs_config.get("poll_interval_seconds"),
                }
            }
        )
