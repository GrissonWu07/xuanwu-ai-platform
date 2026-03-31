from core.management_worker import (
    SUPPORTED_MANAGEMENT_JOB_TYPES as SUPPORTED_PLATFORM_JOB_TYPES,
)
from core.management_worker import shutdown, startup, WorkerSettings as ManagementWorkerSettings


async def run_platform_job(ctx: dict, job_message: dict):
    job_type = job_message["job_type"]
    if job_type not in SUPPORTED_PLATFORM_JOB_TYPES:
        result = {
            "status": "failed",
            "job_type": job_type,
            "error": "unsupported_platform_job_type",
        }
        client = ctx["management_client"]
        await client.fail_job_run(job_message["job_run_id"], result)
        return result

    from core.management_worker import run_management_job

    return await run_management_job(ctx, job_message)


class WorkerSettings(ManagementWorkerSettings):
    queue_name = "platform"
    functions = [run_platform_job]
