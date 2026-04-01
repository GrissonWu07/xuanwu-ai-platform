from __future__ import annotations

import json

from core.adapters.base import BaseGatewayAdapter
from core.adapters.exceptions import GatewayConfigurationError, GatewayExecutionError
from core.contracts.models import build_command_result


class MqttAdapter(BaseGatewayAdapter):
    adapter_type = "mqtt"
    display_name = "MQTT Adapter"
    supports_ingest = True
    supported_capabilities = ("switch.on_off", "actuator.mqtt", "sensor.mqtt")

    def __init__(self, *, transport=None):
        self.transport = transport or PahoMqttTransport()

    def validate_command(self, command: dict) -> None:
        super().validate_command(command)
        route = dict(command.get("route") or {})
        if not str(route.get("broker_host") or "").strip():
            raise GatewayConfigurationError("broker_host_required", "route.broker_host is required")
        if not str(route.get("topic") or "").strip():
            raise GatewayConfigurationError("topic_required", "route.topic is required")

    def execute_command(self, command: dict) -> dict:
        route = dict(command.get("route") or {})
        arguments = dict(command.get("arguments") or {})
        payload = route.get("payload_template")
        if payload is None:
            payload = arguments
        payload = _render_payload(payload, arguments)
        publish_result = self.transport.publish(
            broker_host=str(route.get("broker_host") or "").strip(),
            broker_port=int(route.get("broker_port") or 1883),
            topic=str(route.get("topic") or "").strip(),
            payload=payload,
            qos=int(route.get("qos") or 0),
            retain=bool(route.get("retain", False)),
            username=route.get("username"),
            password=route.get("password"),
            client_id=route.get("client_id"),
            timeout_ms=int(route.get("timeout_ms") or 5000),
        )
        if publish_result.get("status") != "published":
            raise GatewayExecutionError(
                "mqtt_publish_failed",
                "MQTT publish failed",
                details=publish_result,
            )
        return build_command_result(
            command,
            adapter_type=self.adapter_type,
            status="succeeded",
            result={
                "device_id": command.get("device_id"),
                "capability_code": command.get("capability_code"),
                "command_name": command.get("command_name"),
                "arguments": arguments,
                "publish_result": publish_result,
            },
        )

    def normalize_broker_message(self, payload: dict) -> dict:
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
        return self.normalize_broker_message(payload)


class PahoMqttTransport:
    def publish(self, **kwargs):
        try:
            from paho.mqtt import publish
        except Exception as exc:
            raise GatewayExecutionError("mqtt_library_missing", "paho-mqtt is required", details={"reason": str(exc)})
        try:
            publish.single(
                kwargs["topic"],
                payload=json.dumps(kwargs["payload"]),
                qos=kwargs["qos"],
                retain=kwargs["retain"],
                hostname=kwargs["broker_host"],
                port=kwargs["broker_port"],
                client_id=kwargs.get("client_id") or "",
                auth=(
                    {"username": kwargs.get("username"), "password": kwargs.get("password")}
                    if kwargs.get("username")
                    else None
                ),
                keepalive=max(int(kwargs["timeout_ms"] / 1000), 1),
            )
            return {"status": "published", "topic": kwargs["topic"], "qos": kwargs["qos"], "retain": kwargs["retain"]}
        except Exception as exc:
            return {"status": "failed", "reason": str(exc)}


def _render_payload(payload, arguments):
    if isinstance(payload, dict):
        return {key: _render_payload(value, arguments) for key, value in payload.items()}
    if isinstance(payload, list):
        return [_render_payload(item, arguments) for item in payload]
    if isinstance(payload, str) and payload.startswith("{arguments.") and payload.endswith("}"):
        path = payload[len("{arguments.") : -1]
        value = arguments
        for part in path.split("."):
            value = value.get(part) if isinstance(value, dict) else None
        return value
    return payload

