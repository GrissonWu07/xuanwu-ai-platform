from __future__ import annotations

import aiohttp


class ManagementClient:
    def __init__(self, config: dict):
        management_config = config.get("management", {})
        self.base_url = management_config["base_url"].rstrip("/")
        self.control_secret = management_config["control_secret"]
        self._session = aiohttp.ClientSession(
            headers={"X-Xuanwu-Control-Secret": self.control_secret}
        )

    async def complete_job_run(self, job_run_id: str, payload: dict):
        async with self._session.post(
            f"{self.base_url}/control-plane/v1/jobs/runs/{job_run_id}:complete",
            json=payload,
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def fail_job_run(self, job_run_id: str, payload: dict):
        async with self._session.post(
            f"{self.base_url}/control-plane/v1/jobs/runs/{job_run_id}:fail",
            json=payload,
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def close(self):
        await self._session.close()
