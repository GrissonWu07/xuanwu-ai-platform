from __future__ import annotations

import json

from aiohttp import web

from config.security import resolve_control_secret
from core.api.base_handler import BaseHandler
from core.store.exceptions import DeviceBindException, DeviceNotFoundException
from core.store.local_store import LocalControlPlaneStore


class ControlPlaneHandler(BaseHandler):
    def __init__(self, config: dict):
        super().__init__(config)
        self.store = LocalControlPlaneStore.from_config(config)
        self.control_secret = resolve_control_secret(config)

    def _verify_control_secret(self, request: web.Request) -> bool:
        expected = str(self.control_secret or "").strip()
        if not expected:
            return False
        provided = request.headers.get("X-Xuanwu-Control-Secret", "").strip()
        return bool(provided) and provided == expected

    def _json_response(self, payload: dict, *, status: int = 200) -> web.Response:
        response = web.Response(
            text=json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
            content_type="application/json",
            status=status,
        )
        self._add_cors_headers(response)
        return response

    async def handle_get_server_config(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        return self._json_response(self.store.load_server_profile())

    async def handle_put_server_config(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        return self._json_response(self.store.save_server_profile(payload))

    async def handle_list_users(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        return self._json_response({"items": self.store.list_users()})

    async def handle_create_user(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        try:
            created = self.store.create_user(payload)
        except ValueError as exc:
            return self._json_response({"error": str(exc)}, status=400)
        return self._json_response(created, status=201)

    async def handle_list_channels(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        return self._json_response({"items": self.store.list_channels()})

    async def handle_create_channel(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        try:
            created = self.store.create_channel(payload)
        except ValueError as exc:
            return self._json_response({"error": str(exc)}, status=400)
        return self._json_response(created, status=201)

    async def handle_get_device(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        device_id = request.match_info["device_id"]
        payload = self.store.get_device(device_id)
        if payload is None:
            return self._json_response({"error": "device_not_found"}, status=404)
        return self._json_response(payload)

    async def handle_put_device(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        device_id = request.match_info["device_id"]
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        return self._json_response(self.store.save_device(device_id, payload))

    async def handle_get_agent(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        agent_id = request.match_info["agent_id"]
        payload = self.store.get_agent(agent_id)
        if payload is None:
            return self._json_response({"error": "agent_not_found"}, status=404)
        return self._json_response(payload)

    async def handle_put_agent(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        agent_id = request.match_info["agent_id"]
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        return self._json_response(self.store.save_agent(agent_id, payload))

    async def handle_post_event(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        try:
            created = self.store.append_event(payload)
        except ValueError as exc:
            return self._json_response({"error": str(exc)}, status=400)
        return self._json_response(created, status=201)

    async def handle_list_events(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        return self._json_response({"items": self.store.list_events()})

    async def handle_post_telemetry(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        try:
            created = self.store.append_telemetry(payload)
        except ValueError as exc:
            return self._json_response({"error": str(exc)}, status=400)
        return self._json_response(created, status=201)

    async def handle_list_telemetry(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        return self._json_response({"items": self.store.list_telemetry()})

    async def handle_list_alarms(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        return self._json_response({"items": self.store.list_alarms()})

    async def handle_ack_alarm(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        alarm_id = str(request.match_info["alarm_id"]).strip()
        if not alarm_id:
            return self._json_response({"error": "alarm_id_required"}, status=400)
        payload = self.store.acknowledge_alarm(alarm_id)
        if payload is None:
            return self._json_response({"error": "alarm_not_found"}, status=404)
        return self._json_response(payload)

    async def handle_list_gateways(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        return self._json_response({"items": self.store.list_gateways()})

    async def handle_get_gateway(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        gateway_id = str(request.match_info["gateway_id"]).strip()
        payload = self.store.get_gateway(gateway_id)
        if payload is None:
            return self._json_response({"error": "gateway_not_found"}, status=404)
        return self._json_response(payload)

    async def handle_upsert_gateway(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        gateway_id = str(request.match_info.get("gateway_id") or "").strip()
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        try:
            saved = self.store.save_gateway(gateway_id or payload.get("gateway_id"), payload)
        except ValueError as exc:
            return self._json_response({"error": str(exc)}, status=400)
        return self._json_response(saved)

    async def handle_list_capabilities(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        return self._json_response({"items": self.store.list_capabilities()})

    async def handle_create_capability(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        try:
            saved = self.store.save_capability(payload.get("capability_id"), payload)
        except ValueError as exc:
            return self._json_response({"error": str(exc)}, status=400)
        return self._json_response(saved, status=201)

    async def handle_list_capability_routes(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        return self._json_response({"items": self.store.list_capability_routes()})

    async def handle_create_capability_route(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        try:
            saved = self.store.save_capability_route(payload.get("route_id"), payload)
        except ValueError as exc:
            return self._json_response({"error": str(exc)}, status=400)
        return self._json_response(saved, status=201)

    async def handle_list_firmwares(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        return self._json_response({"items": self.store.list_firmwares()})

    async def handle_get_firmware(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        firmware_id = str(request.match_info["firmware_id"]).strip()
        payload = self.store.get_firmware(firmware_id)
        if payload is None:
            return self._json_response({"error": "firmware_not_found"}, status=404)
        return self._json_response(payload)

    async def handle_upsert_firmware(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        firmware_id = str(request.match_info.get("firmware_id") or "").strip()
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        try:
            saved = self.store.save_firmware(firmware_id or payload.get("firmware_id"), payload)
        except ValueError as exc:
            return self._json_response({"error": str(exc)}, status=400)
        return self._json_response(saved)

    async def handle_list_ota_campaigns(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        return self._json_response({"items": self.store.list_ota_campaigns()})

    async def handle_create_ota_campaign(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        try:
            saved = self.store.save_ota_campaign(payload.get("campaign_id"), payload)
        except ValueError as exc:
            return self._json_response({"error": str(exc)}, status=400)
        return self._json_response(saved, status=201)

    async def handle_resolve_device_config(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)

        device_id = str(payload.get("device_id", "")).strip()
        client_id = payload.get("client_id")
        selected_module = payload.get("selected_module") or {}
        if not device_id:
            return self._json_response({"error": "device_id_required"}, status=400)

        try:
            resolved = self.store.resolve_device_config(
                self.config,
                device_id=device_id,
                client_id=client_id,
                selected_module=selected_module,
            )
        except DeviceNotFoundException:
            return self._json_response({"error": "device_not_found"}, status=404)
        except DeviceBindException as exc:
            return self._json_response(
                {"error": "device_bind_required", "bind_code": exc.bind_code},
                status=409,
            )

        resolved_config = resolved["resolved_config"]
        return self._json_response(
            {
                "device": resolved["device"],
                "binding": resolved.get("binding", {}),
                "agent": resolved["agent"],
                "plugins": resolved_config.get("plugins", {}),
                "context_providers": resolved_config.get("context_providers", []),
                "voiceprint": resolved_config.get("voiceprint", {}),
                "summaryMemory": resolved_config.get("summaryMemory", {}),
                "resolved_config": resolved_config,
            }
        )

    async def handle_report_chat_history(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)

        session_id = str(payload.get("session_id", "")).strip()
        if not session_id:
            return self._json_response({"error": "session_id_required"}, status=400)
        record = self.store.append_chat_history(session_id, payload)
        return self._json_response(record, status=201)

    async def handle_generate_chat_summary(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            payload = {}

        summary_id = str(request.match_info["summary_id"]).strip()
        if not summary_id:
            return self._json_response({"error": "summary_id_required"}, status=400)
        record = self.store.save_summary_request(summary_id, payload)
        return self._json_response(record, status=202)
