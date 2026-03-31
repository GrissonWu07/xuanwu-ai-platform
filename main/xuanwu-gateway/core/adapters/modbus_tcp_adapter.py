from __future__ import annotations

from core.adapters.base import BaseGatewayAdapter
from core.adapters.exceptions import GatewayConfigurationError, GatewayExecutionError
from core.contracts.models import build_command_result


class ModbusTcpAdapter(BaseGatewayAdapter):
    adapter_type = "modbus_tcp"
    display_name = "Modbus TCP Adapter"
    supports_dry_run = False
    supported_capabilities = (
        "industrial.register.read",
        "industrial.register.write",
        "industrial.coil.write",
    )

    def __init__(self, *, transport=None):
        self.transport = transport or PymodbusTransport()

    def validate_command(self, command: dict) -> None:
        super().validate_command(command)
        route = dict(command.get("route") or {})
        if not str(route.get("host") or "").strip():
            raise GatewayConfigurationError("host_required", "route.host is required")
        if route.get("address") is None:
            raise GatewayConfigurationError("address_required", "route.address is required")

    def execute_command(self, command: dict) -> dict:
        route = dict(command.get("route") or {})
        response = self.transport.request(
            function=str(command.get("command_name") or "").strip(),
            host=str(route.get("host") or "").strip(),
            port=int(route.get("port") or 502),
            unit_id=int(route.get("unit_id") or 1),
            address=int(route.get("address")),
            quantity=int(route.get("quantity") or 1),
            value=(command.get("arguments") or {}).get("value"),
            timeout_ms=int(route.get("timeout_ms") or 5000),
        )
        if response.get("status") != "ok":
            raise GatewayExecutionError("modbus_request_failed", "Modbus TCP request failed", details=response)
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


class PymodbusTransport:
    def request(self, **kwargs):
        try:
            from pymodbus.client import ModbusTcpClient
        except Exception as exc:
            raise GatewayExecutionError("modbus_library_missing", "pymodbus is required", details={"reason": str(exc)})
        client = ModbusTcpClient(kwargs["host"], port=kwargs["port"], timeout=max(kwargs["timeout_ms"] / 1000.0, 0.1))
        try:
            if not client.connect():
                return {"status": "failed", "reason": "connect_failed"}
            function = kwargs["function"]
            if function == "read_holding_registers":
                response = client.read_holding_registers(kwargs["address"], count=kwargs["quantity"], slave=kwargs["unit_id"])
                values = list(response.registers or []) if not response.isError() else None
                return {"status": "ok" if not response.isError() else "failed", "values": values}
            if function == "write_single_register":
                response = client.write_register(kwargs["address"], kwargs["value"], slave=kwargs["unit_id"])
                return {"status": "ok" if not response.isError() else "failed"}
            if function == "write_single_coil":
                response = client.write_coil(kwargs["address"], bool(kwargs["value"]), slave=kwargs["unit_id"])
                return {"status": "ok" if not response.isError() else "failed"}
            return {"status": "failed", "reason": "unsupported_function"}
        finally:
            client.close()
