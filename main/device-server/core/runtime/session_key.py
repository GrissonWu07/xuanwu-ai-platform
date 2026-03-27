from __future__ import annotations


def _normalize(value: str | None, fallback: str) -> str:
    if value is None:
        return fallback
    normalized = str(value).strip().replace(":", "-")
    return normalized or fallback


def build_atlas_session_key(
    device_id: str | None,
    client_id: str | None = None,
    *,
    agent_id: str = "main",
    channel: str = "xiaozhi",
) -> str:
    device_key = _normalize(device_id, "unknown-device")
    user_id = f"device-{device_key}"
    base = f"agent:{agent_id}:user:{user_id}:{channel}:dm:{device_key}"

    client_key = _normalize(client_id, "")
    if client_key:
        return f"{base}:topic:{client_key}"
    return base
