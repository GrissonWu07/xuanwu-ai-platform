from __future__ import annotations

from core.adapters.exceptions import GatewayConfigurationError
from core.adapters.http_adapter import HttpAdapter


class HomeAssistantAdapter(HttpAdapter):
    adapter_type = "home_assistant"
    display_name = "Home Assistant Adapter"
    supported_capabilities = ("switch.on_off", "light.brightness", "home_assistant.service")

    def validate_command(self, command: dict) -> None:
        route = dict(command.get("route") or {})
        base_url = str(route.get("base_url") or "").strip()
        token = str(route.get("token") or "").strip()
        entity_id = str(route.get("entity_id") or "").strip()
        if str(command.get("command_name") or "").strip() == "read_state":
            if not base_url:
                raise GatewayConfigurationError("base_url_required", "route.base_url is required")
            if not token:
                raise GatewayConfigurationError("token_required", "route.token is required")
            if not entity_id:
                raise GatewayConfigurationError("entity_id_required", "route.entity_id is required")
            super().validate_command(self._translate_command(command))
            return
        service_domain = str(route.get("service_domain") or "").strip()
        service_name = str(route.get("service_name") or "").strip()
        if not base_url:
            raise GatewayConfigurationError("base_url_required", "route.base_url is required")
        if not token:
            raise GatewayConfigurationError("token_required", "route.token is required")
        if not service_domain or not service_name:
            raise GatewayConfigurationError("service_required", "route.service_domain and route.service_name are required")
        if not entity_id:
            raise GatewayConfigurationError("entity_id_required", "route.entity_id is required")

    def execute_command(self, command: dict) -> dict:
        return super().execute_command(self._translate_command(command))

    def _translate_command(self, command: dict) -> dict:
        route = dict(command.get("route") or {})
        if str(command.get("command_name") or "").strip() == "read_state":
            translated = dict(command)
            translated["route"] = {
                "url": f"{str(route.get('base_url') or '').rstrip('/')}/api/states/{route.get('entity_id')}",
                "method": "GET",
                "headers": {"Authorization": f"Bearer {route.get('token')}"},
                "timeout_ms": route.get("timeout_ms", 5000),
            }
            return translated
        data = dict(route.get("data") or {})
        data.setdefault("entity_id", route.get("entity_id"))
        data.update(dict(command.get("arguments") or {}))
        translated = dict(command)
        translated["route"] = {
            "url": f"{str(route.get('base_url') or '').rstrip('/')}/api/services/{route.get('service_domain')}/{route.get('service_name')}",
            "method": "POST",
            "headers": {"Authorization": f"Bearer {route.get('token')}", "Content-Type": "application/json"},
            "body_template": data,
            "timeout_ms": route.get("timeout_ms", 5000),
        }
        return translated

