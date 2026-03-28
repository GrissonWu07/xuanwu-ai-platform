from __future__ import annotations

import asyncio

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
            "X-Xiaozhi-Control-Plane-Secret": self.control_plane_secret,
            "X-Request-Id": request_id,
        }

    async def list_agents(self, request_id: str):
        return await self._get_json("/xuanwu/v1/admin/agents", request_id)

    async def list_model_providers(self, request_id: str):
        return await self._get_json("/xuanwu/v1/admin/model-providers", request_id)

    async def list_models(self, request_id: str):
        return await self._get_json("/xuanwu/v1/admin/models", request_id)

    async def _get_json(self, path: str, request_id: str):
        if not self.base_url:
            return 503, {
                "ok": False,
                "error": {"code": "xuanwu_base_url_missing"},
            }

        timeout = ClientTimeout(total=self.timeout_seconds)
        try:
            async with ClientSession(timeout=timeout) as session:
                async with session.get(
                    f"{self.base_url}{path}",
                    headers=self.build_headers(request_id),
                ) as response:
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
