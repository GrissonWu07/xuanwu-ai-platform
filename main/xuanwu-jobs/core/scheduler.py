from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from config.settings import load_runtime_config
from core.clients.management_client import ManagementClient
from core.queue import create_redis_queue, enqueue_message, get_queue_name


def parse_timestamp(value: str) -> datetime:
    normalized = str(value).replace("Z", "+00:00")
    return datetime.fromisoformat(normalized).astimezone(timezone.utc)


def format_timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


class JobScheduler:
    def __init__(self, *, client, redis_queue, config: dict):
        self.client = client
        self.redis_queue = redis_queue
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
            queue_name = get_queue_name(self.config, claimed["executor_type"])
            function_name = (
                "run_platform_job"
                if claimed["executor_type"] == "platform"
                else "run_external_job"
            )
            await enqueue_message(self.redis_queue, function_name, queue_name, claimed)


async def run_scheduler_forever():
    config = load_runtime_config()
    client = ManagementClient(config)
    redis_queue = await create_redis_queue(config["jobs"]["redis_url"])
    scheduler = JobScheduler(client=client, redis_queue=redis_queue, config=config)
    try:
        while True:
            await scheduler.run_once()
            await asyncio.sleep(config["jobs"]["poll_interval_seconds"])
    finally:
        await client.close()
        close = getattr(redis_queue, "close", None)
        if callable(close):
            result = close()
            if asyncio.iscoroutine(result):
                await result


def main():
    asyncio.run(run_scheduler_forever())


if __name__ == "__main__":
    main()
