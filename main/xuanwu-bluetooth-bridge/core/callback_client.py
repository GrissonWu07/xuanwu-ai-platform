from __future__ import annotations

import aiohttp


class GatewayCallbackClient:
    def __init__(self, config: dict):
        gateway_config = config.get("gateway", {})
        self.base_url = str(gateway_config.get("callback_base_url") or "").rstrip("/")
        token = str(gateway_config.get("callback_token") or "").strip()
        self._headers = {}
        if token:
            self._headers["X-Xuanwu-Control-Secret"] = token
        self._session = None

    async def _get_session(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(headers=self._headers)
        return self._session

    async def post_http_push(self, payload: dict):
        if not self.base_url:
            return {"status": "skipped"}
        session = await self._get_session()
        async with session.post(
            f"{self.base_url}/gateway/v1/ingest/http-push",
            json=payload,
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def post_bridge_event(self, payload: dict):
        if not self.base_url:
            return {"status": "skipped"}
        session = await self._get_session()
        async with session.post(
            f"{self.base_url}/gateway/v1/bridge/events",
            json=payload,
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def post_command_result(self, payload: dict):
        if not self.base_url:
            return {"status": "skipped"}
        session = await self._get_session()
        async with session.post(
            f"{self.base_url}/gateway/v1/commands:dispatch-result",
            json=payload,
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def close(self):
        if self._session is not None and not self._session.closed:
            await self._session.close()


class NullGatewayCallbackClient:
    async def post_http_push(self, payload: dict):
        return payload

    async def post_bridge_event(self, payload: dict):
        return payload

    async def post_command_result(self, payload: dict):
        return payload

    async def close(self):
        return None
