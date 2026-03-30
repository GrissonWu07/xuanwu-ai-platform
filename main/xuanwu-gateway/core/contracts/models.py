from __future__ import annotations

from copy import deepcopy
from typing import Any


def build_command_result(command: dict[str, Any], *, adapter_type: str, status: str = "accepted") -> dict[str, Any]:
    return {
        "request_id": command.get("request_id"),
        "gateway_id": command.get("gateway_id"),
        "adapter_type": adapter_type,
        "status": status,
        "result": {
            "device_id": command.get("device_id"),
            "capability_code": command.get("capability_code"),
            "command_name": command.get("command_name"),
            "arguments": deepcopy(command.get("arguments") or {}),
        },
        "events": [],
        "telemetry": [],
    }

