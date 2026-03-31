from __future__ import annotations

import os

import aiohttp

from config.config_loader import load_config
from core.runtime.session_registry import runtime_session_registry
from core.utils.cache.config import CacheType
from core.utils.cache.manager import cache_manager


class ManagementClient:
    def __init__(self, *, base_url: str, control_secret: str):
        self.base_url = base_url.rstrip("/")
        self._session = aiohttp.ClientSession(
            headers={"X-Xuanwu-Control-Secret": control_secret}
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


def load_worker_config() -> dict:
    return {
        "management": {
            "base_url": (
                os.environ.get("XUANWU_MANAGEMENT_SERVER_URL", "").strip()
                or "http://xuanwu-management-server:18082"
            ),
            "control_secret": (
                os.environ.get("XUANWU_MANAGEMENT_SERVER_SECRET", "").strip()
                or "xuanwu-management-local-secret"
            ),
        }
    }


async def run_device_job(ctx: dict, job_message: dict):
    job_type = str(job_message.get("job_type", "")).strip()
    payload = dict(job_message.get("payload", {}))
    job_run_id = str(job_message.get("job_run_id", "")).strip()
    management_client = ctx.get("management_client")

    if job_type == "runtime_config_refresh":
        cache_manager.clear(CacheType.CONFIG)
        config = load_config()
        result = {
            "status": "completed",
            "job_type": job_type,
            "result": {
                "selected_module": config.get("selected_module", {}),
                "server": config.get("server", {}),
            },
        }
        if management_client is not None and job_run_id:
            await management_client.complete_job_run(job_run_id, result)
        return result

    if job_type == "runtime_session_unregister":
        runtime_session_id = str(payload.get("runtime_session_id", "")).strip()
        if not runtime_session_id:
            result = {
                "status": "failed",
                "job_type": job_type,
                "error": "runtime_session_id_required",
            }
            if management_client is not None and job_run_id:
                await management_client.fail_job_run(job_run_id, result)
            return result
        runtime_session_registry.unregister(runtime_session_id)
        result = {
            "status": "completed",
            "job_type": job_type,
            "result": {"runtime_session_id": runtime_session_id, "status": "removed"},
        }
        if management_client is not None and job_run_id:
            await management_client.complete_job_run(job_run_id, result)
        return result

    result = {
        "status": "failed",
        "job_type": job_type,
        "error": "unsupported_device_job_type",
    }
    if management_client is not None and job_run_id:
        await management_client.fail_job_run(job_run_id, result)
    return result


async def startup(ctx: dict):
    config = load_worker_config()
    ctx["management_client"] = ManagementClient(
        base_url=config["management"]["base_url"],
        control_secret=config["management"]["control_secret"],
    )


async def shutdown(ctx: dict):
    await ctx["management_client"].close()


class DeviceWorkerSettings:
    queue_name = "device"
    functions = [run_device_job]
    on_startup = startup
    on_shutdown = shutdown
