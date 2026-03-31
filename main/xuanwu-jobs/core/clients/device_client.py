from __future__ import annotations

from aiohttp import ClientSession


class DeviceRuntimeClient:
    def __init__(self, config: dict):
        device = config.get("device", {})
        self.base_url = str(device.get("base_url", "")).rstrip("/")
        self.runtime_secret = str(device.get("runtime_secret", "")).strip()
        headers = {}
        if self.runtime_secret:
            headers["X-Xuanwu-Runtime-Secret"] = self.runtime_secret
        self.session = ClientSession(headers=headers)

    async def close(self):
        await self.session.close()

    async def execute_job(self, job_message: dict):
        async with self.session.post(
            f"{self.base_url}/runtime/v1/jobs:execute",
            json=job_message,
        ) as response:
            return await response.json()
