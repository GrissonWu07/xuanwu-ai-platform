from __future__ import annotations

import json

from aiohttp import ClientSession


class ManagementClient:
    def __init__(self, config: dict):
        management = config.get("management", {})
        self.base_url = str(management.get("base_url", "")).rstrip("/")
        self.control_secret = str(management.get("control_secret", "")).strip()
        self.session = ClientSession(
            headers={"X-Xuanwu-Control-Secret": self.control_secret}
        )

    async def close(self):
        await self.session.close()

    async def list_due_schedules(self, *, now_iso: str, limit: int):
        async with self.session.get(
            f"{self.base_url}/control-plane/v1/jobs/schedules:due",
            params={"now": now_iso, "limit": str(limit)},
        ) as response:
            return await response.json()

    async def claim_schedule(self, schedule_id: str, *, scheduled_for: str):
        async with self.session.post(
            f"{self.base_url}/control-plane/v1/jobs/schedules/{schedule_id}:claim",
            json={"scheduled_for": scheduled_for},
        ) as response:
            return await response.json()

    async def list_dispatchable_job_runs(self, *, now_iso: str, limit: int):
        async with self.session.get(
            f"{self.base_url}/control-plane/v1/jobs/runs:dispatchable",
            params={"now": now_iso, "limit": str(limit)},
        ) as response:
            return await response.json()

    async def claim_job_run(self, job_run_id: str, *, started_at: str):
        async with self.session.post(
            f"{self.base_url}/control-plane/v1/jobs/runs/{job_run_id}:claim",
            json={"started_at": started_at},
        ) as response:
            return await response.json()

    async def execute_job(self, job_message: dict):
        async with self.session.post(
            f"{self.base_url}/control-plane/v1/jobs:execute",
            json=job_message,
        ) as response:
            return await response.json()

    async def complete_job_run(self, job_run_id: str, payload: dict):
        async with self.session.post(
            f"{self.base_url}/control-plane/v1/jobs/runs/{job_run_id}:complete",
            json=payload,
        ) as response:
            return await response.json()

    async def fail_job_run(self, job_run_id: str, payload: dict):
        async with self.session.post(
            f"{self.base_url}/control-plane/v1/jobs/runs/{job_run_id}:fail",
            json=payload,
        ) as response:
            return await response.json()
