from __future__ import annotations

import json

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
        result = adapter.ingest(payload)
        if result.get("error"):
            return result, 400
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
        payload.setdefault("adapter_type", "sensor_mqtt")
        result, status = await self._ingest_payload(payload)
        return self._json_response(result, status=status)

    async def handle_health(self, request: web.Request) -> web.Response:
        return self._json_response({"status": "ok", "adapter_count": len(self.registry.describe())})

    async def handle_get_config(self, request: web.Request) -> web.Response:
        return self._json_response(self.config)

    async def handle_get_device_state(self, request: web.Request) -> web.Response:
        device_id = str(request.match_info["device_id"]).strip()
        payload = self.device_state.get(device_id, {"device_id": device_id, "status": "unknown"})
        return self._json_response(payload)
