from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from config.settings import load_runtime_config
from core.clients.device_client import DeviceRuntimeClient
from core.clients.gateway_client import GatewayClient
from core.clients.management_client import ManagementClient
from core.dispatcher import JobDispatcher


def parse_timestamp(value: str) -> datetime:
    normalized = str(value).replace("Z", "+00:00")
    return datetime.fromisoformat(normalized).astimezone(timezone.utc)


def format_timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


class JobScheduler:
    def __init__(self, *, client, dispatcher, config: dict):
        self.client = client
        self.dispatcher = dispatcher
        self.config = config

    async def run_once(self, *, now: datetime | None = None):
        current_time = now or datetime.now(timezone.utc)
        now_iso = format_timestamp(current_time)
        limit = int(self.config.get("jobs", {}).get("schedule_batch_size", 100))
        due_response = await self.client.list_due_schedules(now_iso=now_iso, limit=limit)
        for schedule in due_response.get("items", []):
            claimed = await self.client.claim_schedule(
                schedule["schedule_id"],
                scheduled_for=schedule.get("next_run_at", now_iso),
            )
            await self._dispatch_job(claimed)
        dispatchable_response = await self.client.list_dispatchable_job_runs(now_iso=now_iso, limit=limit)
        for job_run in dispatchable_response.get("items", []):
            claimed_run = await self.client.claim_job_run(
                job_run["job_run_id"],
                started_at=job_run.get("scheduled_for", now_iso),
            )
            await self._dispatch_job(claimed_run)

    async def _dispatch_job(self, job_message: dict):
        result = await self.dispatcher.dispatch(job_message)
        normalized = str(job_message.get("executor_type", "")).strip().lower()
        if normalized not in {"platform", "management"}:
            if str(result.get("status", "")).lower() in {"accepted", "completed", "ok"}:
                complete = getattr(self.client, "complete_job_run", None)
                if callable(complete):
                    await complete(
                        job_message["job_run_id"],
                        {
                            "status": "completed",
                            "result": result,
                        },
                    )
            else:
                fail = getattr(self.client, "fail_job_run", None)
                if callable(fail):
                    await fail(
                        job_message["job_run_id"],
                        {
                            "status": "failed",
                            "error": result.get("error", "job_dispatch_failed"),
                            "result": result,
                        },
                    )


async def run_scheduler_forever():
    config = load_runtime_config()
    client = ManagementClient(config)
    dispatcher = JobDispatcher(
        management_client=client,
        gateway_client=GatewayClient(config),
        device_client=DeviceRuntimeClient(config),
    )
    scheduler = JobScheduler(client=client, dispatcher=dispatcher, config=config)
    try:
        while True:
            await scheduler.run_once()
            await asyncio.sleep(config["jobs"]["poll_interval_seconds"])
    finally:
        await client.close()
        await dispatcher.gateway_client.close()
        await dispatcher.device_client.close()


def main():
    asyncio.run(run_scheduler_forever())


if __name__ == "__main__":
    main()
