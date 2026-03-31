from __future__ import annotations

import json
from urllib import request as urllib_request
from urllib.error import HTTPError, URLError

from core.adapters.base import BaseGatewayAdapter
from core.adapters.exceptions import GatewayConfigurationError, GatewayExecutionError
from core.contracts.models import build_command_result


class NearlinkAdapter(BaseGatewayAdapter):
    adapter_type = "nearlink"
    display_name = "NearLink Adapter"
    supports_dry_run = False
    supported_capabilities = ("wireless.nearlink.command", "wireless.nearlink.state")

    def __init__(self, *, transport=None):
        self.transport = transport or NearlinkBridgeTransport()

    def validate_command(self, command: dict) -> None:
        super().validate_command(command)
        route = dict(command.get("route") or {})
        if not str(route.get("bridge_url") or "").strip():
            raise GatewayConfigurationError("bridge_url_required", "route.bridge_url is required")
        if not str(route.get("link_id") or "").strip():
            raise GatewayConfigurationError("link_id_required", "route.link_id is required")

    def execute_command(self, command: dict) -> dict:
        route = dict(command.get("route") or {})
        response = self.transport.request(
            bridge_url=str(route.get("bridge_url") or "").rstrip("/"),
            link_id=str(route.get("link_id") or "").strip(),
            action=str(command.get("command_name") or "").strip(),
            payload=dict(command.get("arguments") or {}),
            timeout_ms=int(route.get("timeout_ms") or 5000),
        )
        if response.get("status") != "ok":
            raise GatewayExecutionError("nearlink_request_failed", "NearLink request failed", details=response)
        return build_command_result(
            command,
            adapter_type=self.adapter_type,
            status="succeeded",
            result={
                "device_id": command.get("device_id"),
                "capability_code": command.get("capability_code"),
                "command_name": command.get("command_name"),
                "arguments": command.get("arguments") or {},
                "protocol_response": response,
            },
        )


class NearlinkBridgeTransport:
    def request(self, **kwargs):
        req = urllib_request.Request(
            url=f"{kwargs['bridge_url']}/nearlink/commands",
            data=json.dumps({"link_id": kwargs["link_id"], "action": kwargs["action"], "payload": kwargs["payload"]}).encode("utf-8"),
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib_request.urlopen(req, timeout=max(kwargs["timeout_ms"] / 1000.0, 0.1)) as response:
                body = response.read()
                return {"status": "ok", "body": json.loads(body.decode("utf-8")) if body else {}}
        except HTTPError as exc:
            return {"status": "failed", "status_code": exc.code}
        except URLError as exc:
            raise GatewayExecutionError("nearlink_transport_error", "NearLink bridge transport error", details={"reason": str(exc)})
