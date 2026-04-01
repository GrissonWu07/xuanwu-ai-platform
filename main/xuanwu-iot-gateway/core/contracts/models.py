from __future__ import annotations

from copy import deepcopy
from typing import Any


def build_command_result(
    command: dict[str, Any],
    *,
    adapter_type: str,
    status: str = "accepted",
    result: dict[str, Any] | None = None,
    events: list[dict[str, Any]] | None = None,
    telemetry: list[dict[str, Any]] | None = None,
    error: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "request_id": command.get("request_id"),
        "gateway_id": command.get("gateway_id"),
        "adapter_type": adapter_type,
        "status": status,
        "result": result
        or {
            "device_id": command.get("device_id"),
            "capability_code": command.get("capability_code"),
            "command_name": command.get("command_name"),
            "arguments": deepcopy(command.get("arguments") or {}),
        },
        "events": deepcopy(events or []),
        "telemetry": deepcopy(telemetry or []),
        "error": deepcopy(error),
    }


def build_error_result(
    command: dict[str, Any],
    *,
    adapter_type: str,
    error_code: str,
    message: str,
    status: str = "failed",
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return build_command_result(
        command,
        adapter_type=adapter_type,
        status=status,
        error={
            "code": error_code,
            "message": message,
            "details": deepcopy(details or {}),
        },
    )

