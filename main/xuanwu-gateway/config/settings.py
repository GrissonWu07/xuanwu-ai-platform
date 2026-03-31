import os


def load_runtime_config() -> dict:
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
        },
        "jobs": {
            "redis_url": (
                os.environ.get("XUANWU_JOBS_REDIS_URL", "").strip()
                or "redis://redis:6379/0"
            ),
        },
    }
