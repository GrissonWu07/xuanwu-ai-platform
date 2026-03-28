from __future__ import annotations

import json

from aiohttp import web

from config.config_loader import resolve_control_secret
from core.api.base_handler import BaseHandler
from core.control_plane.exceptions import DeviceBindException, DeviceNotFoundException
from core.control_plane.local_store import LocalControlPlaneStore


class ControlPlaneHandler(BaseHandler):
    def __init__(self, config: dict):
        super().__init__(config)
        self.store = LocalControlPlaneStore.from_config(config)
        self.control_secret = resolve_control_secret(config)

    def _verify_control_secret(self, request: web.Request) -> bool:
        expected = str(self.control_secret or "").strip()
        if not expected:
            return False
        provided = request.headers.get("X-Xiaozhi-Control-Secret", "").strip()
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
                "agent": resolved["agent"],
                "plugins": resolved_config.get("plugins", {}),
                "context_providers": resolved_config.get("context_providers", []),
                "voiceprint": resolved_config.get("voiceprint", {}),
                "summaryMemory": resolved_config.get("summaryMemory", {}),
                "resolved_config": resolved_config,
            }
        )
