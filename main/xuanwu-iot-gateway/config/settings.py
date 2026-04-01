import os


def load_runtime_config() -> dict:
    return {
        "server": {
            "host": os.environ.get("XUANWU_GATEWAY_HOST", "0.0.0.0").strip() or "0.0.0.0",
            "http_port": int(os.environ.get("XUANWU_GATEWAY_PORT", "18084")),
        },
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
    }
