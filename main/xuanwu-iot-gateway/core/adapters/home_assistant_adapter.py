from __future__ import annotations

from core.adapters.exceptions import GatewayConfigurationError
from core.adapters.http_adapter import HttpAdapter


class HomeAssistantAdapter(HttpAdapter):
    adapter_type = "home_assistant"
    display_name = "Home Assistant Adapter"
    supports_ingest = True
    supported_capabilities = ("switch.on_off", "light.brightness", "home_assistant.service", "home_assistant.state")

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

    def validate_ingest_payload(self, payload: dict) -> None:
        if not str(payload.get("device_id") or "").strip():
            raise GatewayConfigurationError("device_id_required", "device_id is required")
        if not str(payload.get("gateway_id") or "").strip():
            raise GatewayConfigurationError("gateway_id_required", "gateway_id is required")
        if not str(payload.get("entity_id") or "").strip():
            raise GatewayConfigurationError("entity_id_required", "entity_id is required")
        if not isinstance(payload.get("state"), dict):
            raise GatewayConfigurationError("state_required", "state object is required")

    def normalize_ingest(self, payload: dict) -> dict:
        state = dict(payload.get("state") or {})
        attributes = dict(state.get("attributes") or {})
        telemetry_payload = {
            "telemetry_id": payload.get("telemetry_id") or f"telemetry-{payload.get('device_id')}",
            "device_id": payload.get("device_id"),
            "gateway_id": payload.get("gateway_id"),
            "capability_code": payload.get("capability_code") or "home_assistant.state",
            "observed_at": payload.get("observed_at"),
            "metrics": {
                "state": state.get("state"),
                **attributes,
            },
        }
        event_payload = {
            "event_id": payload.get("event_id") or f"event-{payload.get('device_id')}",
            "device_id": payload.get("device_id"),
            "gateway_id": payload.get("gateway_id"),
            "event_type": "home_assistant.state_changed",
            "severity": "info",
            "occurred_at": payload.get("observed_at"),
            "payload": {
                "entity_id": payload.get("entity_id"),
                "state": state.get("state"),
                "attributes": attributes,
            },
        }
        return {
            "status": "accepted",
            "telemetry": [telemetry_payload],
            "events": [event_payload],
        }

