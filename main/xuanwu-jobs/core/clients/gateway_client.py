from __future__ import annotations

from aiohttp import ClientSession


class GatewayClient:
    def __init__(self, config: dict):
        gateway = config.get("gateway", {})
        self.base_url = str(gateway.get("base_url", "")).rstrip("/")
        self.control_secret = str(gateway.get("control_secret", "")).strip()
        headers = {}
        if self.control_secret:
            headers["X-Xuanwu-Control-Secret"] = self.control_secret
        self.session = ClientSession(headers=headers)

    async def close(self):
        await self.session.close()

    async def execute_job(self, job_message: dict):
        async with self.session.post(
            f"{self.base_url}/gateway/v1/jobs:execute",
            json=job_message,
        ) as response:
            return await response.json()
