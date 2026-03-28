import json
import uuid

from aiohttp import web

from core.api.base_handler import BaseHandler
from core.clients.xuanwu_client import XuanWuClient


class XuanWuProxyHandler(BaseHandler):
    def __init__(self, config: dict):
        super().__init__(config)
        self.client = XuanWuClient(config)

    def _request_id(self, request: web.Request) -> str:
        return request.headers.get("X-Request-Id", "").strip() or uuid.uuid4().hex

    def _json_response(self, payload: dict, *, status: int) -> web.Response:
        response = web.Response(
            text=json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
            content_type="application/json",
            status=status,
        )
        self._add_cors_headers(response)
        return response

    async def handle_agents(self, request: web.Request) -> web.Response:
        status, payload = await self.client.list_agents(self._request_id(request))
        return self._json_response(payload, status=status)

    async def handle_model_providers(self, request: web.Request) -> web.Response:
        status, payload = await self.client.list_model_providers(self._request_id(request))
        return self._json_response(payload, status=status)

    async def handle_models(self, request: web.Request) -> web.Response:
        status, payload = await self.client.list_models(self._request_id(request))
        return self._json_response(payload, status=status)
