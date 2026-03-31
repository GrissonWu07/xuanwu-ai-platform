from __future__ import annotations

from typing import Any


def get_queue_name(config: dict, executor_type: str) -> str:
    queue_names = config.get("jobs", {}).get("queue_names", {})
    return queue_names.get(executor_type, executor_type)


async def enqueue_message(redis_queue: Any, function_name: str, queue_name: str, message: dict):
    return await redis_queue.enqueue_job(function_name, message, _queue_name=queue_name)


async def create_redis_queue(redis_url: str):
    from arq.connections import RedisSettings, create_pool

    settings = RedisSettings.from_dsn(redis_url)
    return await create_pool(settings)
