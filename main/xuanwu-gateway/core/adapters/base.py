from __future__ import annotations

from typing import Any

from core.contracts.models import build_command_result


class BaseGatewayAdapter:
    adapter_type = "base"
    display_name = "Base Adapter"
    supports_dry_run = True

    def describe(self) -> dict[str, Any]:
        return {
            "adapter_type": self.adapter_type,
            "display_name": self.display_name,
            "supports_dry_run": self.supports_dry_run,
        }

    def dispatch(self, command: dict[str, Any]) -> dict[str, Any]:
        return build_command_result(command, adapter_type=self.adapter_type)

