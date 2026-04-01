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
        "state": {
            "backend": os.environ.get("XUANWU_IOT_STATE_BACKEND", "postgres").strip() or "postgres",
            "postgres": {
                "url": os.environ.get("XUANWU_IOT_PG_URL", "").strip(),
                "host": os.environ.get("XUANWU_PG_HOST", "postgres").strip() or "postgres",
                "port": int(os.environ.get("XUANWU_PG_PORT", "5432")),
                "database": os.environ.get("XUANWU_PG_DB", "xuanwu_platform").strip() or "xuanwu_platform",
                "user": os.environ.get("XUANWU_PG_USER", "xuanwu").strip() or "xuanwu",
                "password": (
                    os.environ.get("XUANWU_PG_PASSWORD", "xuanwu_local_password").strip()
                    or "xuanwu_local_password"
                ),
                "schema": os.environ.get("XUANWU_IOT_PG_SCHEMA", "xw_iot").strip() or "xw_iot",
            },
        },
    }
