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
        if not str(route.get("device_key") or route.get("link_id") or "").strip():
            raise GatewayConfigurationError("device_key_required", "route.device_key is required")

    def execute_command(self, command: dict) -> dict:
        route = dict(command.get("route") or {})
        device_key = str(route.get("device_key") or route.get("link_id") or "").strip()
        operation = str(route.get("operation") or command.get("command_name") or "").strip().lower()
        response = self.transport.request(
            bridge_url=str(route.get("bridge_url") or "").rstrip("/"),
            bridge_token=str(route.get("bridge_token") or "").strip(),
            device_key=device_key,
            gateway_id=command.get("gateway_id"),
            device_id=command.get("device_id"),
            request_id=command.get("request_id"),
            command_type=route.get("command_type") or "capability.invoke",
            capability_code=command.get("capability_code"),
            action=str(command.get("command_name") or "").strip(),
            operation=operation,
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
        operation = str(kwargs.get("operation") or "").lower()
        endpoint = f"/nearlink/v1/devices/{kwargs['device_key']}:command"
        if operation in {"query_state", "read_state", "query-state"}:
            endpoint = f"/nearlink/v1/devices/{kwargs['device_key']}:query-state"
        req = urllib_request.Request(
            url=f"{kwargs['bridge_url']}{endpoint}",
            data=json.dumps(
                {
                    "request_id": kwargs.get("request_id"),
                    "gateway_id": kwargs.get("gateway_id"),
                    "device_id": kwargs.get("device_id"),
                    "command_type": kwargs.get("command_type"),
                    "capability_code": kwargs.get("capability_code"),
                    "action": kwargs["action"],
                    "arguments": kwargs["payload"],
                }
            ).encode("utf-8"),
            method="POST",
            headers=self._build_headers(kwargs.get("bridge_token")),
        )
        try:
            with urllib_request.urlopen(req, timeout=max(kwargs["timeout_ms"] / 1000.0, 0.1)) as response:
                body = response.read()
                return {"status": "ok", "body": json.loads(body.decode("utf-8")) if body else {}}
        except HTTPError as exc:
            return {"status": "failed", "status_code": exc.code}
        except URLError as exc:
            raise GatewayExecutionError("nearlink_transport_error", "NearLink bridge transport error", details={"reason": str(exc)})

    def _build_headers(self, bridge_token: str | None) -> dict:
        headers = {"Content-Type": "application/json"}
        token = str(bridge_token or "").strip()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers
