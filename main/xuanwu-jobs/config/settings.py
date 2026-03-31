import os


def load_runtime_config() -> dict:
    host = os.environ.get("XUANWU_JOBS_HOST", "0.0.0.0").strip() or "0.0.0.0"
    port = int(os.environ.get("XUANWU_JOBS_PORT", "18083"))
    management_base_url = (
        os.environ.get("XUANWU_MANAGEMENT_SERVER_URL", "").strip()
        or "http://xuanwu-management-server:18082"
    )
    management_secret = (
        os.environ.get("XUANWU_MANAGEMENT_SERVER_SECRET", "").strip()
        or "xuanwu-management-local-secret"
    )
    redis_url = os.environ.get("XUANWU_JOBS_REDIS_URL", "").strip() or "redis://redis:6379/0"
    batch_size = int(os.environ.get("XUANWU_JOBS_BATCH_SIZE", "100"))
    poll_interval = float(os.environ.get("XUANWU_JOBS_POLL_INTERVAL_SECONDS", "2"))

    return {
        "server": {"host": host, "http_port": port},
        "management": {
            "base_url": management_base_url,
            "control_secret": management_secret,
        },
        "jobs": {
            "redis_url": redis_url,
            "schedule_batch_size": batch_size,
            "poll_interval_seconds": poll_interval,
            "queue_names": {
                "platform": "platform",
                "agent": "agent",
                "gateway": "gateway",
            },
        },
    }
