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
        if status == 204:
            response = web.Response(status=status)
            self._add_cors_headers(response)
            return response
        response = web.Response(
            text=json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
            content_type="application/json",
            status=status,
        )
        self._add_cors_headers(response)
        return response

    async def _optional_json_payload(self, request: web.Request):
        if request.method in {"POST", "PUT", "PATCH"}:
            try:
                return await request.json()
            except Exception:
                return None
        return None

    def _query_params(self, request: web.Request) -> dict[str, str]:
        return {key: value for key, value in request.query.items()}

    async def handle_agents(self, request: web.Request) -> web.Response:
        status, payload = await self.client.list_agents(self._request_id(request))
        return self._json_response(payload, status=status)

    async def handle_model_providers(self, request: web.Request) -> web.Response:
        status, payload = await self.client.list_model_providers(self._request_id(request))
        return self._json_response(payload, status=status)

    async def handle_models(self, request: web.Request) -> web.Response:
        status, payload = await self.client.list_models(self._request_id(request))
        return self._json_response(payload, status=status)

    async def handle_agent_collection(self, request: web.Request) -> web.Response:
        status, payload = await self.client.request_agents(
            request.method,
            self._request_id(request),
            payload=await self._optional_json_payload(request),
            query=self._query_params(request),
        )
        return self._json_response(payload, status=status)

    async def handle_agent_item(self, request: web.Request) -> web.Response:
        status, payload = await self.client.request_agents(
            request.method,
            self._request_id(request),
            payload=await self._optional_json_payload(request),
            agent_id=request.match_info["agent_id"],
            query=self._query_params(request),
        )
        return self._json_response(payload, status=status)

    async def handle_model_provider_collection(self, request: web.Request) -> web.Response:
        status, payload = await self.client.request_model_providers(
            request.method,
            self._request_id(request),
            payload=await self._optional_json_payload(request),
            query=self._query_params(request),
        )
        return self._json_response(payload, status=status)

    async def handle_model_provider_item(self, request: web.Request) -> web.Response:
        status, payload = await self.client.request_model_providers(
            request.method,
            self._request_id(request),
            payload=await self._optional_json_payload(request),
            provider_id=request.match_info["provider_id"],
            query=self._query_params(request),
        )
        return self._json_response(payload, status=status)

    async def handle_model_collection(self, request: web.Request) -> web.Response:
        status, payload = await self.client.request_models(
            request.method,
            self._request_id(request),
            payload=await self._optional_json_payload(request),
            query=self._query_params(request),
        )
        return self._json_response(payload, status=status)

    async def handle_model_item(self, request: web.Request) -> web.Response:
        status, payload = await self.client.request_models(
            request.method,
            self._request_id(request),
            payload=await self._optional_json_payload(request),
            model_id=request.match_info["model_id"],
            query=self._query_params(request),
        )
        return self._json_response(payload, status=status)
