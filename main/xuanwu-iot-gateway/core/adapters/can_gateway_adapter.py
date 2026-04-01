from __future__ import annotations

import json
from urllib import request as urllib_request
from urllib.error import HTTPError, URLError

from core.adapters.base import BaseGatewayAdapter
from core.adapters.exceptions import GatewayConfigurationError, GatewayExecutionError
from core.contracts.models import build_command_result


class CanGatewayAdapter(BaseGatewayAdapter):
    adapter_type = "can_gateway"
    display_name = "CAN Gateway Adapter"
    supports_dry_run = False
    supported_capabilities = ("industrial.frame.command", "industrial.frame.query")

    def __init__(self, *, transport=None):
        self.transport = transport or CanHttpBridgeTransport()

    def validate_command(self, command: dict) -> None:
        super().validate_command(command)
        route = dict(command.get("route") or {})
        if not str(route.get("bridge_url") or "").strip():
            raise GatewayConfigurationError("bridge_url_required", "route.bridge_url is required")
        if route.get("frame_id") is None:
            raise GatewayConfigurationError("frame_id_required", "route.frame_id is required")

    def execute_command(self, command: dict) -> dict:
        route = dict(command.get("route") or {})
        response = self.transport.request(
            bridge_url=str(route.get("bridge_url") or "").rstrip("/"),
            channel=str(route.get("channel") or "").strip(),
            frame_id=int(route.get("frame_id")),
            dlc=int(route.get("dlc") or 8),
            data=list((command.get("arguments") or {}).get("data") or []),
            action=str(command.get("command_name") or "").strip(),
            timeout_ms=int(route.get("timeout_ms") or 5000),
        )
        if response.get("status") != "ok":
            raise GatewayExecutionError("can_gateway_request_failed", "CAN gateway request failed", details=response)
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


class CanHttpBridgeTransport:
    def request(self, **kwargs):
        payload = {
            "channel": kwargs["channel"],
            "frame_id": kwargs["frame_id"],
            "dlc": kwargs["dlc"],
            "data": kwargs["data"],
        }
        data = json.dumps(payload).encode("utf-8")
        path = "/frames/query" if kwargs.get("action") == "query_frame_state" else "/frames"
        req = urllib_request.Request(
            url=f"{kwargs['bridge_url']}{path}",
            data=data,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib_request.urlopen(req, timeout=max(kwargs["timeout_ms"] / 1000.0, 0.1)) as response:
                body = response.read()
                return {
                    "status": "ok",
                    "status_code": response.status,
                    "body": json.loads(body.decode("utf-8")) if body else {},
                    "frame_id": kwargs["frame_id"],
                    "acknowledged": True,
                }
        except HTTPError as exc:
            return {"status": "failed", "status_code": exc.code}
        except URLError as exc:
            raise GatewayExecutionError("can_gateway_transport_error", "CAN bridge transport error", details={"reason": str(exc)})
