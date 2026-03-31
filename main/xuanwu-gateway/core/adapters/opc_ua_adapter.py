from __future__ import annotations

from core.adapters.base import BaseGatewayAdapter
from core.adapters.exceptions import GatewayConfigurationError, GatewayExecutionError
from core.contracts.models import build_command_result


class OpcUaAdapter(BaseGatewayAdapter):
    adapter_type = "opc_ua"
    display_name = "OPC UA Adapter"
    supports_dry_run = False
    supported_capabilities = ("industrial.node.read", "industrial.node.write")

    def __init__(self, *, transport=None):
        self.transport = transport or OpcUaTransport()

    def validate_command(self, command: dict) -> None:
        super().validate_command(command)
        route = dict(command.get("route") or {})
        if not str(route.get("endpoint") or "").strip():
            raise GatewayConfigurationError("endpoint_required", "route.endpoint is required")
        if not str(route.get("node_id") or "").strip():
            raise GatewayConfigurationError("node_id_required", "route.node_id is required")

    def execute_command(self, command: dict) -> dict:
        route = dict(command.get("route") or {})
        response = self.transport.request(
            action=str(command.get("command_name") or "").strip(),
            endpoint=str(route.get("endpoint") or "").strip(),
            node_id=str(route.get("node_id") or "").strip(),
            value=(command.get("arguments") or {}).get("value"),
            timeout_ms=int(route.get("timeout_ms") or 5000),
        )
        if response.get("status") != "ok":
            raise GatewayExecutionError("opcua_request_failed", "OPC UA request failed", details=response)
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


class OpcUaTransport:
    def request(self, **kwargs):
        try:
            from opcua import Client
        except Exception as exc:
            raise GatewayExecutionError("opcua_library_missing", "opcua library is required", details={"reason": str(exc)})
        client = Client(kwargs["endpoint"], timeout=max(kwargs["timeout_ms"] / 1000.0, 0.1))
        try:
            client.connect()
            node = client.get_node(kwargs["node_id"])
            if kwargs["action"] == "read_node":
                return {"status": "ok", "value": node.get_value()}
            if kwargs["action"] == "write_node":
                node.set_value(kwargs["value"])
                return {"status": "ok", "value": kwargs["value"]}
            return {"status": "failed", "reason": "unsupported_action"}
        finally:
            client.disconnect()
