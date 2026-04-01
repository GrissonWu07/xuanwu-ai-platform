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
        if not str(route.get("device_key") or route.get("device_address") or "").strip():
            raise GatewayConfigurationError("device_key_required", "route.device_key is required")
        if not str(route.get("service_uuid") or "").strip():
            raise GatewayConfigurationError("service_uuid_required", "route.service_uuid is required")
        if not str(route.get("characteristic_uuid") or "").strip():
            raise GatewayConfigurationError("characteristic_uuid_required", "route.characteristic_uuid is required")

    def execute_command(self, command: dict) -> dict:
        route = dict(command.get("route") or {})
        operation = str(route.get("operation") or command.get("command_name") or "").strip().lower()
        device_key = str(route.get("device_key") or route.get("device_address") or "").strip()
        response = self.transport.request(
            bridge_url=str(route.get("bridge_url") or "").rstrip("/"),
            bridge_token=str(route.get("bridge_token") or "").strip(),
            device_key=device_key,
            service_uuid=str(route.get("service_uuid") or "").strip(),
            characteristic_uuid=str(route.get("characteristic_uuid") or "").strip(),
            operation=operation,
            gateway_id=command.get("gateway_id"),
            device_id=command.get("device_id"),
            request_id=command.get("request_id"),
            encoding=str(route.get("encoding") or (command.get("arguments") or {}).get("encoding") or "hex"),
            value=(command.get("arguments") or {}).get("value", route.get("value")),
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
            "service_uuid": kwargs["service_uuid"],
            "characteristic_uuid": kwargs["characteristic_uuid"],
            "request_id": kwargs.get("request_id"),
            "gateway_id": kwargs.get("gateway_id"),
            "device_id": kwargs.get("device_id"),
            "encoding": kwargs.get("encoding"),
            "value": kwargs["value"],
        }
        operation = str(kwargs.get("operation") or "").lower()
        endpoint = "write"
        if operation in {"read", "read_characteristic"}:
            endpoint = "read"
        elif operation in {"subscribe", "subscribe_characteristic"}:
            endpoint = "subscribe"
        elif operation in {"unsubscribe", "unsubscribe_characteristic"}:
            endpoint = "unsubscribe"
        req = urllib_request.Request(
            url=f"{kwargs['bridge_url']}/bluetooth/v1/devices/{kwargs['device_key']}/characteristics:{endpoint}",
            data=json.dumps(payload).encode("utf-8"),
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
            raise GatewayExecutionError("bluetooth_transport_error", "Bluetooth bridge transport error", details={"reason": str(exc)})

    def _build_headers(self, bridge_token: str | None) -> dict:
        headers = {"Content-Type": "application/json"}
        token = str(bridge_token or "").strip()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers
