from __future__ import annotations

import aiohttp
from aiohttp import ClientResponseError


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

    async def post_event(self, payload: dict):
        async with self._session.post(
            f"{self.base_url}/control-plane/v1/gateway/events",
            json=payload,
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def post_telemetry(self, payload: dict):
        async with self._session.post(
            f"{self.base_url}/control-plane/v1/gateway/telemetry",
            json=payload,
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def post_command_result(self, payload: dict):
        async with self._session.post(
            f"{self.base_url}/control-plane/v1/gateway/command-results",
            json=payload,
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def upsert_discovered_device(self, payload: dict):
        async with self._session.post(
            f"{self.base_url}/control-plane/v1/gateway/device-discovery",
            json=payload,
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def post_device_heartbeat(self, device_id: str, payload: dict) -> bool:
        try:
            async with self._session.post(
                f"{self.base_url}/control-plane/v1/devices/{device_id}:heartbeat",
                json=payload,
            ) as response:
                response.raise_for_status()
                await response.json()
                return True
        except ClientResponseError as exc:
            if exc.status == 404:
                return False
            raise

    async def close(self):
        await self._session.close()


class NullManagementClient:
    async def complete_job_run(self, job_run_id: str, payload: dict):
        return {"job_run_id": job_run_id, "payload": payload}

    async def fail_job_run(self, job_run_id: str, payload: dict):
        return {"job_run_id": job_run_id, "payload": payload}

    async def post_event(self, payload: dict):
        return payload

    async def post_telemetry(self, payload: dict):
        return payload

    async def post_command_result(self, payload: dict):
        return payload

    async def upsert_discovered_device(self, payload: dict):
        return payload

    async def post_device_heartbeat(self, device_id: str, payload: dict) -> bool:
        return False

    async def close(self):
        return None
