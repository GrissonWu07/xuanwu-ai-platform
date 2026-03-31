from __future__ import annotations

from config.settings import load_runtime_config
from core.clients.management_client import ManagementClient
from core.registry.adapter_registry import create_builtin_registry


async def run_gateway_job(ctx: dict, job_message: dict):
    client = ctx["management_client"]
    registry = ctx.get("adapter_registry") or create_builtin_registry()
    job_run_id = job_message["job_run_id"]
    payload = dict(job_message.get("payload", {}))
    adapter_type = str(payload.get("adapter_type", "")).strip()

    if not adapter_type:
        result = {"status": "failed", "error": "adapter_type_required"}
        await client.fail_job_run(job_run_id, result)
        return result

    adapter = registry.get(adapter_type)
    if adapter is None:
        result = {"status": "failed", "error": "adapter_not_found"}
        await client.fail_job_run(job_run_id, result)
        return result

    result = adapter.dispatch(payload)
    await client.complete_job_run(job_run_id, result)
    return result


async def startup(ctx: dict):
    config = load_runtime_config()
    ctx["management_client"] = ManagementClient(config)
    ctx["adapter_registry"] = create_builtin_registry()


async def shutdown(ctx: dict):
    await ctx["management_client"].close()


class GatewayWorkerSettings:
    queue_name = "gateway"
    functions = [run_gateway_job]
    on_startup = startup
    on_shutdown = shutdown
