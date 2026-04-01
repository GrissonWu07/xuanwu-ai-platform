from __future__ import annotations

import json
from datetime import datetime, timezone

from aiohttp import web

from core.clients.management_client import ManagementClient, NullManagementClient
from core.registry.adapter_registry import create_builtin_registry


class GatewayHandler:
    def __init__(self, config: dict, *, registry=None, management_client=None):
        self.config = config
        self.registry = registry or create_builtin_registry()
        self.device_state: dict[str, dict] = {}
        if management_client is not None:
            self.management_client = management_client
        elif config.get("management", {}).get("base_url"):
            self.management_client = ManagementClient(config)
        else:
            self.management_client = NullManagementClient()

    def _json_response(self, payload: dict, *, status: int = 200) -> web.Response:
        return web.Response(
            text=json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
            content_type="application/json",
            status=status,
        )

    def _loads_json(self, payload: str) -> dict:
        return json.loads(payload)

    def _timestamp(self, value=None) -> str:
        if value:
            return str(value)
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def _infer_device_kind(self, payload: dict) -> str:
        declared = str(payload.get("device_kind", "")).strip()
        if declared:
            return declared
        adapter_type = str(payload.get("adapter_type", "")).strip()
        capability_code = str(payload.get("capability_code", "")).strip()
        if adapter_type.startswith("sensor") or capability_code.startswith("sensor."):
            return "sensor"
        if adapter_type in {"modbus_tcp", "opc_ua", "bacnet_ip", "can_gateway"}:
            return "industrial"
        return "actuator"

    async def _sync_device_presence(
        self,
        payload: dict,
        *,
        observed_at=None,
        session_status: str = "gateway_active",
    ) -> None:
        device_id = str(payload.get("device_id", "")).strip()
        if not device_id:
            return
        adapter_type = str(payload.get("adapter_type", "")).strip() or "gateway"
        gateway_id = str(payload.get("gateway_id", "")).strip() or None
        last_seen_at = self._timestamp(observed_at or payload.get("observed_at"))
        runtime_endpoint = f"/gateway/v1/devices/{device_id}/state"
        managed = await self.management_client.post_device_heartbeat(
            device_id,
            {
                "status": "online",
                "session_status": session_status,
                "last_seen_at": last_seen_at,
                "gateway_id": gateway_id,
                "runtime_endpoint": runtime_endpoint,
                "protocol_type": payload.get("protocol_type") or adapter_type,
                "adapter_type": adapter_type,
            },
        )
        if managed:
            return
        await self.management_client.upsert_discovered_device(
            {
                "discovery_id": str(
                    payload.get("discovery_id") or f"gateway:{gateway_id or 'unknown'}:{device_id}"
                ),
                "device_id": device_id,
                "display_name": payload.get("display_name"),
                "ingress_type": "gateway",
                "device_kind": self._infer_device_kind(payload),
                "gateway_id": gateway_id,
                "protocol_type": payload.get("protocol_type") or adapter_type,
                "adapter_type": adapter_type,
                "runtime_endpoint": runtime_endpoint,
                "first_seen_at": last_seen_at,
                "last_seen_at": last_seen_at,
                "source_payload": {
                    "capability_code": payload.get("capability_code"),
                    "topic": payload.get("topic"),
                    "site_id": payload.get("site_id"),
                },
            }
        )

    def _dispatch_command_payload(self, payload: dict) -> tuple[dict, int]:
        adapter_type = str(payload.get("adapter_type", "")).strip()
        if not adapter_type:
            return {"error": "adapter_type_required"}, 400

        adapter = self.registry.get(adapter_type)
        if adapter is None:
            return {"error": "adapter_not_found"}, 404
        result = adapter.dispatch(payload)
        device_id = str(payload.get("device_id", "")).strip()
        if device_id:
            self.device_state[device_id] = {
                "device_id": device_id,
                "last_request_id": payload.get("request_id"),
                "last_command_name": payload.get("command_name"),
                "status": result.get("status", "accepted"),
            }
        return result, 200

    async def _publish_command_result(self, result: dict) -> None:
        if result.get("error"):
            status = result.get("status", "failed")
        else:
            status = result.get("status", "succeeded")
        payload = {
            "result_id": result.get("request_id"),
            "command_id": result.get("request_id"),
            "trace_id": result.get("request_id"),
            "device_id": result.get("result", {}).get("device_id"),
            "gateway_id": result.get("gateway_id"),
            "status": status,
            "finished_at": None,
            "result": result.get("result"),
            "error": result.get("error"),
        }
        await self.management_client.post_command_result(payload)

    async def _ingest_payload(self, payload: dict) -> tuple[dict, int]:
        adapter_type = str(payload.get("adapter_type", "")).strip()
        if not adapter_type:
            return {"error": "adapter_type_required"}, 400
        adapter = self.registry.get(adapter_type)
        if adapter is None:
            return {"error": "adapter_not_found"}, 404
        if hasattr(adapter, "ingest"):
            result = adapter.ingest(payload)
        elif hasattr(adapter, "normalize_broker_message"):
            result = adapter.normalize_broker_message(payload)
        else:
            return {"error": "adapter_ingest_not_supported"}, 400
        if result.get("error"):
            return result, 400
        await self._sync_device_presence(
            payload,
            observed_at=payload.get("observed_at") or payload.get("reported_at"),
            session_status="telemetry_active",
        )
        for telemetry in result.get("telemetry") or []:
            await self.management_client.post_telemetry(telemetry)
        for event in result.get("events") or []:
            await self.management_client.post_event(event)
        return result, 202

    async def handle_list_adapters(self, request: web.Request) -> web.Response:
        return self._json_response({"items": self.registry.describe()})

    async def handle_dispatch_command(self, request: web.Request) -> web.Response:
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        result, status = self._dispatch_command_payload(payload)
        if status == 200:
            await self._sync_device_presence(payload, session_status="command_ready")
            await self._publish_command_result(result)
        return self._json_response(result, status=status)

    async def handle_command_collection(self, request: web.Request) -> web.Response:
        return await self.handle_dispatch_command(request)

    async def handle_execute_job(self, request: web.Request) -> web.Response:
        try:
            job_message = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        payload = dict(job_message.get("payload") or {})
        payload.setdefault("request_id", job_message.get("job_run_id"))
        result, status = self._dispatch_command_payload(payload)
        if status != 200:
            return self._json_response(result, status=status)
        await self._sync_device_presence(payload, session_status="command_ready")
        await self._publish_command_result(result)
        return self._json_response(
            {
                "status": "completed",
                "executor_type": "gateway",
                "job_run_id": job_message.get("job_run_id"),
                "result": result,
            }
        )

    async def handle_ingest_http_push(self, request: web.Request) -> web.Response:
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        payload.setdefault("adapter_type", "sensor_http_push")
        result, status = await self._ingest_payload(payload)
        return self._json_response(result, status=status)

    async def handle_ingest_mqtt(self, request: web.Request) -> web.Response:
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        payload.setdefault("adapter_type", "mqtt")
        result, status = await self._ingest_payload(payload)
        return self._json_response(result, status=status)

    async def handle_ingest_home_assistant(self, request: web.Request) -> web.Response:
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        payload.setdefault("adapter_type", "home_assistant")
        result, status = await self._ingest_payload(payload)
        return self._json_response(result, status=status)

    async def handle_bridge_event(self, request: web.Request) -> web.Response:
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        device_key = str(payload.get("device_key") or "").strip()
        bridge_type = str(payload.get("bridge_type") or "bridge").strip()
        observed_at = payload.get("timestamp")
        gateway_payload = {
            "device_id": str(payload.get("device_id") or device_key).strip(),
            "gateway_id": payload.get("gateway_id") or payload.get("bridge_id"),
            "adapter_type": bridge_type,
            "protocol_type": bridge_type,
            "device_kind": payload.get("device_kind"),
            "display_name": payload.get("display_name"),
            "discovery_id": payload.get("discovery_id"),
            "observed_at": observed_at,
        }
        await self._sync_device_presence(
            gateway_payload,
            observed_at=observed_at,
            session_status="bridge_active",
        )
        await self.management_client.post_event(
            {
                "event_id": str(
                    payload.get("event_id")
                    or f"bridge-event-{bridge_type}-{device_key or 'unknown'}-{observed_at or 'now'}"
                ),
                "device_id": gateway_payload["device_id"],
                "gateway_id": gateway_payload["gateway_id"],
                "event_type": payload.get("event_type") or "bridge.event",
                "severity": payload.get("severity") or "info",
                "occurred_at": observed_at or self._timestamp(),
                "payload": dict(payload.get("payload") or {}),
            }
        )
        telemetry = payload.get("telemetry")
        if isinstance(telemetry, dict) and telemetry:
            await self.management_client.post_telemetry(
                {
                    "telemetry_id": str(
                        payload.get("telemetry_id")
                        or f"bridge-telemetry-{bridge_type}-{device_key or 'unknown'}-{observed_at or 'now'}"
                    ),
                    "device_id": gateway_payload["device_id"],
                    "gateway_id": gateway_payload["gateway_id"],
                    "capability_code": payload.get("capability_code") or f"bridge.{bridge_type}",
                    "observed_at": observed_at or self._timestamp(),
                    "metrics": telemetry,
                }
            )
        return self._json_response({"status": "accepted"}, status=202)

    async def handle_command_dispatch_result(self, request: web.Request) -> web.Response:
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        device_id = str(
            payload.get("result", {}).get("device_id") or payload.get("device_id") or ""
        ).strip()
        if device_id:
            await self._sync_device_presence(
                {
                    "device_id": device_id,
                    "gateway_id": payload.get("gateway_id"),
                    "adapter_type": payload.get("adapter_type"),
                    "protocol_type": payload.get("adapter_type"),
                    "observed_at": payload.get("finished_at") or payload.get("timestamp"),
                },
                observed_at=payload.get("finished_at") or payload.get("timestamp"),
                session_status="command_ready",
            )
        await self.management_client.post_command_result(payload)
        return self._json_response({"status": "accepted"}, status=202)

    async def handle_health(self, request: web.Request) -> web.Response:
        return self._json_response({"status": "ok", "adapter_count": len(self.registry.describe())})

    async def handle_get_config(self, request: web.Request) -> web.Response:
        return self._json_response(self.config)

    async def handle_get_device_state(self, request: web.Request) -> web.Response:
        device_id = str(request.match_info["device_id"]).strip()
        payload = self.device_state.get(device_id, {"device_id": device_id, "status": "unknown"})
        return self._json_response(payload)
