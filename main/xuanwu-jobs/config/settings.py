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
    gateway_base_url = (
        os.environ.get("XUANWU_GATEWAY_URL", "").strip()
        or "http://xuanwu-gateway:18084"
    )
    gateway_secret = (
        os.environ.get("XUANWU_GATEWAY_SECRET", "").strip()
        or management_secret
    )
    device_base_url = (
        os.environ.get("XUANWU_DEVICE_RUNTIME_URL", "").strip()
        or "http://xuanwu-device-server:8003"
    )
    device_runtime_secret = (
        os.environ.get("XUANWU_DEVICE_RUNTIME_SECRET", "").strip()
        or management_secret
    )
    batch_size = int(os.environ.get("XUANWU_JOBS_BATCH_SIZE", "100"))
    poll_interval = float(os.environ.get("XUANWU_JOBS_POLL_INTERVAL_SECONDS", "2"))

    return {
        "server": {"host": host, "http_port": port},
        "management": {
            "base_url": management_base_url,
            "control_secret": management_secret,
        },
        "gateway": {
            "base_url": gateway_base_url,
            "control_secret": gateway_secret,
        },
        "device": {
            "base_url": device_base_url,
            "runtime_secret": device_runtime_secret,
        },
        "jobs": {
            "schedule_batch_size": batch_size,
            "poll_interval_seconds": poll_interval,
            "dispatch_targets": {
                "platform": management_base_url,
                "management": management_base_url,
                "gateway": gateway_base_url,
                "device": device_base_url,
            },
        },
    }
