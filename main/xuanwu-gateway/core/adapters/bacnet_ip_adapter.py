from __future__ import annotations

from core.adapters.base import BaseGatewayAdapter
from core.adapters.exceptions import GatewayConfigurationError, GatewayExecutionError
from core.contracts.models import build_command_result


class BacnetIpAdapter(BaseGatewayAdapter):
    adapter_type = "bacnet_ip"
    display_name = "BACnet IP Adapter"
    supports_dry_run = False
    supported_capabilities = ("industrial.property.read", "industrial.property.write")

    def __init__(self, *, transport=None):
        self.transport = transport or BacnetTransport()

    def validate_command(self, command: dict) -> None:
        super().validate_command(command)
        route = dict(command.get("route") or {})
        if not str(route.get("address") or "").strip():
            raise GatewayConfigurationError("address_required", "route.address is required")
        if not str(route.get("property_name") or "").strip():
            raise GatewayConfigurationError("property_name_required", "route.property_name is required")
        if route.get("object_instance") is None:
            raise GatewayConfigurationError("object_instance_required", "route.object_instance is required")

    def execute_command(self, command: dict) -> dict:
        route = dict(command.get("route") or {})
        response = self.transport.request(
            action=str(command.get("command_name") or "").strip(),
            address=str(route.get("address") or "").strip(),
            object_type=str(route.get("object_type") or "").strip(),
            object_instance=int(route.get("object_instance")),
            property_name=str(route.get("property_name") or "").strip(),
            value=(command.get("arguments") or {}).get("value"),
            timeout_ms=int(route.get("timeout_ms") or 5000),
        )
        if response.get("status") != "ok":
            raise GatewayExecutionError("bacnet_request_failed", "BACnet/IP request failed", details=response)
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


class BacnetTransport:
    def request(self, **kwargs):
        try:
            import BAC0
        except Exception as exc:
            raise GatewayExecutionError("bacnet_library_missing", "BAC0 is required", details={"reason": str(exc)})
        bacnet = BAC0.lite()
        try:
            target = f"{kwargs['object_type']} {kwargs['object_instance']} {kwargs['property_name']}"
            if kwargs["action"] == "read_property":
                value = bacnet.read(f"{kwargs['address']} {target}")
                return {"status": "ok", "value": value}
            if kwargs["action"] == "write_property":
                bacnet.write(f"{kwargs['address']} {target} {kwargs['value']}")
                return {"status": "ok", "value": kwargs["value"]}
            return {"status": "failed", "reason": "unsupported_action"}
        finally:
            bacnet.disconnect()
