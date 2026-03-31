from __future__ import annotations

from config.settings import load_runtime_config
from core.clients.management_client import ManagementClient

SUPPORTED_MANAGEMENT_JOB_TYPES = {
    "telemetry_rollup",
    "alarm_escalation",
    "ota_campaign_tick",
}


async def run_management_job(ctx: dict, job_message: dict):
    client = ctx["management_client"]
    job_run_id = job_message["job_run_id"]
    job_type = job_message["job_type"]
    payload = job_message.get("payload", {})

    if job_type not in SUPPORTED_MANAGEMENT_JOB_TYPES:
        result = {
            "status": "failed",
            "job_type": job_type,
            "error": "unsupported_management_job_type",
        }
        await client.fail_job_run(job_run_id, result)
        return result

    result = {
        "status": "completed",
        "job_type": job_type,
        "result": {
            **payload,
            "status": "completed",
        },
    }
    await client.complete_job_run(job_run_id, result)
    return result


async def startup(ctx: dict):
    config = load_runtime_config()
    ctx["management_client"] = ManagementClient(config)


async def shutdown(ctx: dict):
    await ctx["management_client"].close()


class WorkerSettings:
    queue_name = "management"
    functions = [run_management_job]
    on_startup = startup
    on_shutdown = shutdown
