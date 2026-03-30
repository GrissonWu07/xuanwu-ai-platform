from __future__ import annotations

import json

from aiohttp import web

from core.registry.adapter_registry import create_builtin_registry


class GatewayHandler:
    def __init__(self, config: dict):
        self.config = config
        self.registry = create_builtin_registry()

    def _json_response(self, payload: dict, *, status: int = 200) -> web.Response:
        return web.Response(
            text=json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
            content_type="application/json",
            status=status,
        )

    def _loads_json(self, payload: str) -> dict:
        return json.loads(payload)

    async def handle_list_adapters(self, request: web.Request) -> web.Response:
        return self._json_response({"items": self.registry.describe()})

    async def handle_dispatch_command(self, request: web.Request) -> web.Response:
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)

        adapter_type = str(payload.get("adapter_type", "")).strip()
        if not adapter_type:
            return self._json_response({"error": "adapter_type_required"}, status=400)

        adapter = self.registry.get(adapter_type)
        if adapter is None:
            return self._json_response({"error": "adapter_not_found"}, status=404)
        return self._json_response(adapter.dispatch(payload))

