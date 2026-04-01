from __future__ import annotations

import json

from aiohttp import web

from core.callback_client import GatewayCallbackClient, NullGatewayCallbackClient
from core.runtime import BluetoothBridgeError, BluetoothBridgeRuntime


class BluetoothBridgeHandler:
    def __init__(self, config: dict, *, runtime=None, callback_client=None):
        self.config = config
        self.bridge_token = str(config.get("bridge", {}).get("auth_token") or "").strip()
        if runtime is not None:
            self.runtime = runtime
            self.callback_client = callback_client or NullGatewayCallbackClient()
        else:
            self.callback_client = callback_client or GatewayCallbackClient(config)
            self.runtime = BluetoothBridgeRuntime(config, callback_client=self.callback_client)

    def _verify_auth(self, request: web.Request) -> bool:
        if not self.bridge_token:
            return True
        header = str(request.headers.get("Authorization") or "").strip()
        return header == f"Bearer {self.bridge_token}"

    def _json_response(self, payload: dict, *, status: int = 200) -> web.Response:
        return web.Response(
            text=json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
            content_type="application/json",
            status=status,
        )

    def _handle_bridge_error(self, exc: BluetoothBridgeError) -> web.Response:
        return self._json_response(
            {
                "ok": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                },
            },
            status=exc.status,
        )

    async def handle_health(self, request: web.Request) -> web.Response:
        return self._json_response(
            {
                "status": "ok",
                "bridge_id": self.runtime.bridge_id,
                "adapter_count": len(self.runtime.adapters),
                "active_connection_count": len(self.runtime.connections),
                "active_scan_count": len([item for item in self.runtime.scans.values() if item.get("status") == "running"]),
            }
        )

    async def handle_list_adapters(self, request: web.Request) -> web.Response:
        return self._json_response({"items": self.runtime.list_adapters()})

    async def handle_start_scan(self, request: web.Request) -> web.Response:
        if not self._verify_auth(request):
            return self._json_response({"error": "auth_token_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            payload = {}
        try:
            result = await self.runtime.start_scan(payload)
        except BluetoothBridgeError as exc:
            return self._handle_bridge_error(exc)
        return self._json_response(result, status=201)

    async def handle_stop_scan(self, request: web.Request) -> web.Response:
        if not self._verify_auth(request):
            return self._json_response({"error": "auth_token_invalid"}, status=401)
        try:
            result = self.runtime.stop_scan(str(request.match_info["scan_id"]).strip())
        except BluetoothBridgeError as exc:
            return self._handle_bridge_error(exc)
        return self._json_response(result)

    async def handle_get_scan(self, request: web.Request) -> web.Response:
        try:
            result = self.runtime.get_scan(str(request.match_info["scan_id"]).strip())
        except BluetoothBridgeError as exc:
            return self._handle_bridge_error(exc)
        return self._json_response(result)

    async def handle_list_devices(self, request: web.Request) -> web.Response:
        return self._json_response({"items": self.runtime.list_devices()})

    async def handle_get_device(self, request: web.Request) -> web.Response:
        try:
            result = self.runtime.get_device(str(request.match_info["device_key"]).strip())
        except BluetoothBridgeError as exc:
            return self._handle_bridge_error(exc)
        return self._json_response(result)

    async def handle_connect_device(self, request: web.Request) -> web.Response:
        if not self._verify_auth(request):
            return self._json_response({"error": "auth_token_invalid"}, status=401)
        try:
            result = await self.runtime.connect_device(str(request.match_info["device_key"]).strip())
        except BluetoothBridgeError as exc:
            return self._handle_bridge_error(exc)
        return self._json_response(result)

    async def handle_disconnect_device(self, request: web.Request) -> web.Response:
        if not self._verify_auth(request):
            return self._json_response({"error": "auth_token_invalid"}, status=401)
        try:
            result = await self.runtime.disconnect_device(str(request.match_info["device_key"]).strip())
        except BluetoothBridgeError as exc:
            return self._handle_bridge_error(exc)
        return self._json_response(result)

    async def _read_payload(self, request: web.Request) -> dict:
        try:
            return await request.json()
        except Exception:
            raise BluetoothBridgeError("invalid_json", "The request payload is not valid JSON.")

    async def handle_read_characteristic(self, request: web.Request) -> web.Response:
        if not self._verify_auth(request):
            return self._json_response({"error": "auth_token_invalid"}, status=401)
        try:
            payload = await self._read_payload(request)
            result = self.runtime.read_characteristic(str(request.match_info["device_key"]).strip(), payload)
        except BluetoothBridgeError as exc:
            return self._handle_bridge_error(exc)
        return self._json_response(result)

    async def handle_write_characteristic(self, request: web.Request) -> web.Response:
        if not self._verify_auth(request):
            return self._json_response({"error": "auth_token_invalid"}, status=401)
        try:
            payload = await self._read_payload(request)
            result = await self.runtime.write_characteristic(str(request.match_info["device_key"]).strip(), payload)
        except BluetoothBridgeError as exc:
            return self._handle_bridge_error(exc)
        return self._json_response(result)

    async def handle_subscribe_characteristic(self, request: web.Request) -> web.Response:
        if not self._verify_auth(request):
            return self._json_response({"error": "auth_token_invalid"}, status=401)
        try:
            payload = await self._read_payload(request)
            result = await self.runtime.subscribe_characteristic(str(request.match_info["device_key"]).strip(), payload)
        except BluetoothBridgeError as exc:
            return self._handle_bridge_error(exc)
        return self._json_response(result, status=201)

    async def handle_unsubscribe_characteristic(self, request: web.Request) -> web.Response:
        if not self._verify_auth(request):
            return self._json_response({"error": "auth_token_invalid"}, status=401)
        try:
            payload = await self._read_payload(request)
            result = self.runtime.unsubscribe_characteristic(str(request.match_info["device_key"]).strip(), payload)
        except BluetoothBridgeError as exc:
            return self._handle_bridge_error(exc)
        return self._json_response(result)
