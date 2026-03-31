from __future__ import annotations

import json
from urllib import request as urllib_request
from urllib.error import HTTPError, URLError

from core.adapters.base import BaseGatewayAdapter
from core.adapters.exceptions import GatewayConfigurationError, GatewayExecutionError
from core.contracts.models import build_command_result


class BluetoothAdapter(BaseGatewayAdapter):
    adapter_type = "bluetooth"
    display_name = "Bluetooth Adapter"
    supports_dry_run = False
    supported_capabilities = ("wireless.characteristic.read", "wireless.characteristic.write")

    def __init__(self, *, transport=None):
        self.transport = transport or BluetoothBridgeTransport()

    def validate_command(self, command: dict) -> None:
        super().validate_command(command)
        route = dict(command.get("route") or {})
        if not str(route.get("bridge_url") or "").strip():
            raise GatewayConfigurationError("bridge_url_required", "route.bridge_url is required")
        if not str(route.get("device_address") or "").strip():
            raise GatewayConfigurationError("device_address_required", "route.device_address is required")
        if not str(route.get("characteristic_uuid") or "").strip():
            raise GatewayConfigurationError("characteristic_uuid_required", "route.characteristic_uuid is required")

    def execute_command(self, command: dict) -> dict:
        route = dict(command.get("route") or {})
        response = self.transport.request(
            bridge_url=str(route.get("bridge_url") or "").rstrip("/"),
            device_address=str(route.get("device_address") or "").strip(),
            service_uuid=str(route.get("service_uuid") or "").strip(),
            characteristic_uuid=str(route.get("characteristic_uuid") or "").strip(),
            action=str(command.get("command_name") or "").strip(),
            value=(command.get("arguments") or {}).get("value"),
            timeout_ms=int(route.get("timeout_ms") or 5000),
        )
        if response.get("status") != "ok":
            raise GatewayExecutionError("bluetooth_request_failed", "Bluetooth request failed", details=response)
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


class BluetoothBridgeTransport:
    def request(self, **kwargs):
        payload = {
            "device_address": kwargs["device_address"],
            "service_uuid": kwargs["service_uuid"],
            "characteristic_uuid": kwargs["characteristic_uuid"],
            "action": kwargs["action"],
            "value": kwargs["value"],
        }
        req = urllib_request.Request(
            url=f"{kwargs['bridge_url']}/bluetooth/characteristics",
            data=json.dumps(payload).encode("utf-8"),
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
            raise GatewayExecutionError("bluetooth_transport_error", "Bluetooth bridge transport error", details={"reason": str(exc)})
