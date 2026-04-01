from __future__ import annotations

import asyncio
from typing import Any

from aiohttp import ClientError, ClientSession, ClientTimeout


class XuanWuClient:
    def __init__(self, config: dict):
        self.config = config
        self.base_url = str(config.get("xuanwu", {}).get("base_url", "")).rstrip("/")
        self.control_plane_secret = str(
            config.get("xuanwu", {}).get("control_plane_secret", "")
        ).strip()
        self.timeout_seconds = float(
            config.get("xuanwu", {}).get("timeout_seconds", 10)
        )

    def build_headers(self, request_id: str) -> dict[str, str]:
        return {
            "X-Xuanwu-Control-Plane-Secret": self.control_plane_secret,
            "X-Request-Id": request_id,
        }

    async def list_agents(self, request_id: str):
        return await self.request_agents("GET", request_id)

    async def list_model_providers(self, request_id: str):
        return await self.request_model_providers("GET", request_id)

    async def list_models(self, request_id: str):
        return await self.request_models("GET", request_id)

    async def request_agents(
        self,
        method: str,
        request_id: str,
        *,
        payload: dict[str, Any] | None = None,
        agent_id: str | None = None,
        query: dict[str, str] | None = None,
    ):
        path = "/xuanwu/v1/admin/agents"
        if agent_id:
            path = f"{path}/{agent_id}"
        return await self._request_json(method, path, request_id, payload=payload, query=query)

    async def request_model_providers(
        self,
        method: str,
        request_id: str,
        *,
        payload: dict[str, Any] | None = None,
        provider_id: str | None = None,
        query: dict[str, str] | None = None,
    ):
        path = "/xuanwu/v1/admin/model-providers"
        if provider_id:
            path = f"{path}/{provider_id}"
        return await self._request_json(method, path, request_id, payload=payload, query=query)

    async def request_models(
        self,
        method: str,
        request_id: str,
        *,
        payload: dict[str, Any] | None = None,
        model_id: str | None = None,
        query: dict[str, str] | None = None,
    ):
        path = "/xuanwu/v1/admin/models"
        if model_id:
            path = f"{path}/{model_id}"
        return await self._request_json(method, path, request_id, payload=payload, query=query)

    async def _request_json(
        self,
        method: str,
        path: str,
        request_id: str,
        *,
        payload: dict[str, Any] | None = None,
        query: dict[str, str] | None = None,
    ):
        if not self.base_url:
            return 503, {
                "ok": False,
                "error": {"code": "xuanwu_base_url_missing"},
            }

        timeout = ClientTimeout(total=self.timeout_seconds)
        try:
            async with ClientSession(timeout=timeout) as session:
                async with session.request(
                    method.upper(),
                    f"{self.base_url}{path}",
                    headers=self.build_headers(request_id),
                    json=payload,
                    params=query,
                ) as response:
                    if response.status == 204:
                        return 204, {}
                    try:
                        payload = await response.json()
                    except Exception:
                        payload = {
                            "ok": False,
                            "error": {
                                "code": "xuanwu_invalid_response",
                                "message": await response.text(),
                            },
                        }
                    return response.status, payload
        except asyncio.TimeoutError:
            return 504, {
                "ok": False,
                "error": {"code": "xuanwu_timeout"},
            }
        except ClientError as exc:
            return 502, {
                "ok": False,
                "error": {"code": "xuanwu_unreachable", "message": str(exc)},
            }
