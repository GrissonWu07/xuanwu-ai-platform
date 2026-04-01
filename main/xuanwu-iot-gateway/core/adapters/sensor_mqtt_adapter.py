from __future__ import annotations

from core.adapters.base import BaseGatewayAdapter
from core.adapters.exceptions import GatewayConfigurationError


class SensorMqttAdapter(BaseGatewayAdapter):
    adapter_type = "sensor_mqtt"
    display_name = "Sensor MQTT Adapter"
    supports_dry_run = False
    supports_ingest = True
    supported_capabilities = ("sensor.mqtt", "sensor.temperature", "sensor.humidity")

    def validate_ingest_payload(self, payload: dict) -> None:
        if not str(payload.get("device_id") or "").strip():
            raise GatewayConfigurationError("device_id_required", "device_id is required")
        if not str(payload.get("gateway_id") or "").strip():
            raise GatewayConfigurationError("gateway_id_required", "gateway_id is required")
        if not str(payload.get("topic") or "").strip():
            raise GatewayConfigurationError("topic_required", "topic is required")
        if not isinstance(payload.get("telemetry"), dict):
            raise GatewayConfigurationError("telemetry_required", "telemetry object is required")

    def normalize_ingest(self, payload: dict) -> dict:
        telemetry_payload = {
            "telemetry_id": payload.get("telemetry_id") or f"telemetry-{payload.get('device_id')}",
            "device_id": payload.get("device_id"),
            "gateway_id": payload.get("gateway_id"),
            "capability_code": payload.get("capability_code") or "sensor.mqtt",
            "observed_at": payload.get("observed_at"),
            "metrics": dict(payload.get("telemetry") or {}),
        }
        event_payload = {
            "event_id": payload.get("event_id") or f"event-{payload.get('device_id')}",
            "device_id": payload.get("device_id"),
            "gateway_id": payload.get("gateway_id"),
            "event_type": "telemetry.reported",
            "severity": "info",
            "occurred_at": payload.get("observed_at"),
            "payload": {
                "topic": payload.get("topic"),
                **dict(payload.get("telemetry") or {}),
            },
        }
        return {
            "status": "accepted",
            "telemetry": [telemetry_payload],
            "events": [event_payload],
        }
