import sys
import os
from pathlib import Path

from aiohttp import web

SERVICE_ROOT = Path(__file__).resolve().parent
if str(SERVICE_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVICE_ROOT))

from core.http_server import CONTROL_PLANE_HANDLER_KEY, create_http_app


def create_app(config: dict) -> web.Application:
    return create_http_app(config)


def load_runtime_config() -> dict:
    host = os.environ.get("XUANWU_MANAGEMENT_SERVER_HOST", "0.0.0.0").strip() or "0.0.0.0"
    port = int(os.environ.get("XUANWU_MANAGEMENT_SERVER_PORT", "18082"))
    auth_key = (
        os.environ.get("XUANWU_MANAGEMENT_SERVER_AUTH_KEY", "").strip()
        or "xuanwu-management-local-secret"
    )
    xuanwu_base_url = (
        os.environ.get("XUANWU_BASE_URL", "").strip() or "http://xuanwu-ai:8000"
    )
    xuanwu_control_plane_secret = (
        os.environ.get("XUANWU_CONTROL_PLANE_SECRET", "").strip()
        or "xuanwu-management-to-xuanwu"
    )
    pg_host = os.environ.get("XUANWU_PG_HOST", "postgres").strip() or "postgres"
    pg_port = int(os.environ.get("XUANWU_PG_PORT", "5432"))
    pg_db = os.environ.get("XUANWU_PG_DB", "xuanwu_platform").strip() or "xuanwu_platform"
    pg_user = os.environ.get("XUANWU_PG_USER", "xuanwu").strip() or "xuanwu"
    pg_password = (
        os.environ.get("XUANWU_PG_PASSWORD", "xuanwu_local_password").strip()
        or "xuanwu_local_password"
    )
    pg_schema = os.environ.get("XUANWU_MGMT_PG_SCHEMA", "xw_mgmt").strip() or "xw_mgmt"

    return {
        "server": {
            "host": host,
            "http_port": port,
            "auth_key": auth_key,
        },
        "control-plane": {
            "secret": auth_key,
            "backend": os.environ.get("XUANWU_CONTROL_PLANE_BACKEND", "postgres").strip()
            or "postgres",
            "postgres": {
                "host": pg_host,
                "port": pg_port,
                "database": pg_db,
                "user": pg_user,
                "password": pg_password,
                "schema": pg_schema,
            },
        },
        "xuanwu": {
            "base_url": xuanwu_base_url,
            "control_plane_secret": xuanwu_control_plane_secret,
        },
    }


def main() -> None:
    config = load_runtime_config()
    app = create_app(config)
    web.run_app(
        app,
        host=config["server"]["host"],
        port=config["server"]["http_port"],
    )


if __name__ == "__main__":
    main()
