import os


def _bool_env(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def load_runtime_config() -> dict:
    host = os.environ.get("XUANWU_BLUETOOTH_BRIDGE_HOST", "0.0.0.0").strip() or "0.0.0.0"
    port = int(os.environ.get("XUANWU_BLUETOOTH_BRIDGE_PORT", "19521"))
    auth_token = os.environ.get("XUANWU_BLUETOOTH_BRIDGE_TOKEN", "xuanwu-bluetooth-bridge-secret").strip()
    callback_base_url = (
        os.environ.get("XUANWU_GATEWAY_URL", "").strip()
        or "http://xuanwu-iot-gateway:18084"
    )
    callback_token = (
        os.environ.get("XUANWU_GATEWAY_SECRET", "").strip()
        or "xuanwu-management-local-secret"
    )
    return {
        "server": {"host": host, "http_port": port},
        "bridge": {
            "bridge_id": os.environ.get("XUANWU_BLUETOOTH_BRIDGE_ID", "bluetooth-bridge-local").strip()
            or "bluetooth-bridge-local",
            "auth_token": auth_token,
            "listen_host": host,
            "listen_port": port,
            "platform": {
                "site_id": os.environ.get("XUANWU_PLATFORM_SITE_ID", "site-local").strip() or "site-local",
                "region_id": os.environ.get("XUANWU_PLATFORM_REGION_ID", "region-local").strip() or "region-local",
            },
            "scan": {
                "default_timeout_seconds": int(os.environ.get("XUANWU_BLUETOOTH_SCAN_TIMEOUT", "8")),
                "max_concurrent_scans": int(os.environ.get("XUANWU_BLUETOOTH_MAX_SCANS", "2")),
            },
            "connections": {
                "idle_disconnect_seconds": int(os.environ.get("XUANWU_BLUETOOTH_IDLE_DISCONNECT_SECONDS", "120")),
                "max_active_devices": int(os.environ.get("XUANWU_BLUETOOTH_MAX_ACTIVE_DEVICES", "50")),
            },
            "demo": {
                "enabled": _bool_env("XUANWU_BLUETOOTH_DEMO_ENABLED", True),
                "device_prefix": os.environ.get("XUANWU_BLUETOOTH_DEVICE_PREFIX", "XW-BLE").strip() or "XW-BLE",
            },
        },
        "gateway": {
            "callback_base_url": callback_base_url,
            "callback_token": callback_token,
        },
    }
