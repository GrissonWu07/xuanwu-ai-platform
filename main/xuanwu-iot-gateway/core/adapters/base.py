from __future__ import annotations

from typing import Any

from core.adapters.exceptions import GatewayAdapterError
from core.contracts.models import build_command_result, build_error_result


class BaseGatewayAdapter:
    adapter_type = "base"
    display_name = "Base Adapter"
    supports_dry_run = True
    supports_ingest = False
    supported_capabilities: tuple[str, ...] = ()

    def describe(self) -> dict[str, Any]:
        return {
            "adapter_type": self.adapter_type,
            "display_name": self.display_name,
            "supports_dry_run": self.supports_dry_run,
            "supports_ingest": self.supports_ingest,
            "supported_capabilities": list(self.supported_capabilities),
        }

    def dispatch(self, command: dict[str, Any]) -> dict[str, Any]:
        try:
            self.validate_command(command)
            return self.execute_command(command)
        except GatewayAdapterError as exc:
            return build_error_result(
                command,
                adapter_type=self.adapter_type,
                error_code=exc.code,
                message=exc.message,
                status="failed",
                details=exc.details,
            )

    def validate_command(self, command: dict[str, Any]) -> None:
        if not str(command.get("device_id") or "").strip():
            raise GatewayAdapterError("device_id_required", "device_id is required")
        if not str(command.get("capability_code") or "").strip():
            raise GatewayAdapterError("capability_code_required", "capability_code is required")

    def execute_command(self, command: dict[str, Any]) -> dict[str, Any]:
        return build_command_result(command, adapter_type=self.adapter_type)

    def ingest(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            self.validate_ingest_payload(payload)
            return self.normalize_ingest(payload)
        except GatewayAdapterError as exc:
            return {
                "status": "failed",
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                },
                "events": [],
                "telemetry": [],
            }

    def validate_ingest_payload(self, payload: dict[str, Any]) -> None:
        raise GatewayAdapterError("ingest_not_supported", "adapter does not support ingest", status_code=400)

    def normalize_ingest(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise GatewayAdapterError("ingest_not_supported", "adapter does not support ingest", status_code=400)

