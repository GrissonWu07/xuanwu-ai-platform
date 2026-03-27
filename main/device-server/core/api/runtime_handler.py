
from __future__ import annotations

import json
import uuid
from aiohttp import web

from config.config_loader import resolve_control_secret
from core.api.base_handler import BaseHandler
from core.handle.abortHandle import handleAbortMessage
from core.providers.tts.dto.dto import ContentType, SentenceType, TTSMessageDTO
from core.runtime.session_registry import RuntimeSessionRecord, runtime_session_registry


TAG = __name__


class RuntimeHandler(BaseHandler):
    def __init__(self, config: dict):
        super().__init__(config)
        self.runtime_secret = resolve_control_secret(config)

    def _verify_runtime_secret(self, request: web.Request) -> bool:
        expected = str(self.runtime_secret or "").strip()
        if not expected:
            return False
        provided = request.headers.get("X-Xiaozhi-Runtime-Secret", "").strip()
        return bool(provided) and provided == expected

    def _json_response(self, payload: dict, *, status: int = 200) -> web.Response:
        response = web.Response(
            text=json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
            content_type="application/json",
            status=status,
        )
        self._add_cors_headers(response)
        return response

    def _build_capabilities(self, conn) -> dict:
        available_tools = []
        has_take_photo = False
        func_handler = getattr(conn, "func_handler", None)
        if func_handler and getattr(func_handler, "finish_init", False):
            try:
                available_tools = func_handler.current_support_functions()
                has_take_photo = func_handler.has_tool("self_camera_take_photo")
            except Exception:
                available_tools = []

        return {
            "speaker": conn.tts is not None,
            "camera": has_take_photo,
            "mcp": bool(getattr(conn, "features", None)) or hasattr(conn, "mcp_endpoint_client"),
            "iot": bool(getattr(conn, "iot_descriptors", {})),
            "available_tools": available_tools,
        }

    def _is_connection_gone(self, conn) -> bool:
        stop_event = getattr(conn, "stop_event", None)
        if stop_event is not None and stop_event.is_set():
            return True

        websocket = getattr(conn, "websocket", None)
        if websocket is None:
            return True
        if hasattr(websocket, "closed"):
            return bool(websocket.closed)

        state = getattr(websocket, "state", None)
        return getattr(state, "name", "") == "CLOSED"

    def _bind_status(self, record: RuntimeSessionRecord, conn) -> str:
        if not record.device_id or record.device_id == "unknown-device":
            return "unknown"
        return "pending" if getattr(conn, "need_bind", False) else "bound"

    def _load_record(self, runtime_session_id: str) -> tuple[RuntimeSessionRecord | None, web.Response | None]:
        record = runtime_session_registry.get_by_runtime_session(runtime_session_id)
        if record is None:
            return None, self._json_response({"error": "runtime_session_not_found"}, status=404)
        if self._is_connection_gone(record.conn):
            runtime_session_registry.unregister(runtime_session_id)
            return None, self._json_response({"error": "runtime_session_gone"}, status=410)
        return record, None

    async def handle_context(self, request: web.Request) -> web.Response:
        if not self._verify_runtime_secret(request):
            return self._json_response({"error": "runtime_secret_invalid"}, status=401)

        runtime_session_id = request.match_info["runtime_session_id"]
        record, error_response = self._load_record(runtime_session_id)
        if error_response is not None:
            return error_response

        conn = record.conn
        payload = {
            "runtime_session_id": record.runtime_session_id,
            "device_id": record.device_id,
            "client_id": record.client_id,
            "atlas_session_key": record.atlas_session_key,
            "connected": True,
            "capabilities": self._build_capabilities(conn),
            "state": {
                "is_speaking": bool(getattr(conn, "client_is_speaking", False)),
                "listen_mode": getattr(conn, "client_listen_mode", "auto"),
                "bind_status": self._bind_status(record, conn),
            },
        }
        return self._json_response(payload)

    async def handle_tool_execution(self, request: web.Request) -> web.Response:
        if not self._verify_runtime_secret(request):
            return self._json_response({"error": "runtime_secret_invalid"}, status=401)

        runtime_session_id = request.match_info["runtime_session_id"]
        record, error_response = self._load_record(runtime_session_id)
        if error_response is not None:
            return error_response

        conn = record.conn
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)

        tool_name = str(payload.get("name", "")).strip()
        arguments = payload.get("arguments", {}) or {}
        request_id = payload.get("request_id") or str(uuid.uuid4())

        if not tool_name:
            return self._json_response({"error": "tool_name_required"}, status=400)
        if not getattr(conn, "func_handler", None) or not getattr(conn.func_handler, "finish_init", False):
            return self._json_response({"error": "tool_runtime_not_ready"}, status=409)
        if not conn.func_handler.has_tool(tool_name):
            return self._json_response({"error": "tool_not_found", "name": tool_name}, status=404)

        result = await conn.func_handler.handle_llm_function_call(
            conn,
            {
                "name": tool_name,
                "arguments": arguments,
            },
        )
        action_name = getattr(getattr(result, "action", None), "name", "NONE")
        response_payload = {
            "status": "ok",
            "request_id": request_id,
            "result": {
                "action": action_name,
                "text": getattr(result, "response", None),
                "data": getattr(result, "result", None),
            },
        }
        return self._json_response(response_payload)

    async def handle_interrupt(self, request: web.Request) -> web.Response:
        if not self._verify_runtime_secret(request):
            return self._json_response({"error": "runtime_secret_invalid"}, status=401)

        runtime_session_id = request.match_info["runtime_session_id"]
        record, error_response = self._load_record(runtime_session_id)
        if error_response is not None:
            return error_response

        await handleAbortMessage(record.conn)
        return self._json_response({"status": "ok", "interrupted": True})

    async def handle_speak(self, request: web.Request) -> web.Response:
        if not self._verify_runtime_secret(request):
            return self._json_response({"error": "runtime_secret_invalid"}, status=401)

        runtime_session_id = request.match_info["runtime_session_id"]
        record, error_response = self._load_record(runtime_session_id)
        if error_response is not None:
            return error_response

        conn = record.conn
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)

        text = str(payload.get("text", "")).strip()
        interrupt_current = bool(payload.get("interrupt_current", False))
        if not text:
            return self._json_response({"error": "text_required"}, status=400)
        if conn.tts is None:
            return self._json_response({"error": "tts_not_ready"}, status=409)

        if interrupt_current:
            await handleAbortMessage(conn)

        sentence_id = str(uuid.uuid4().hex)
        conn.sentence_id = sentence_id
        conn.tts.tts_text_queue.put(
            TTSMessageDTO(
                sentence_id=sentence_id,
                sentence_type=SentenceType.FIRST,
                content_type=ContentType.ACTION,
            )
        )
        conn.tts.tts_one_sentence(conn, ContentType.TEXT, content_detail=text)
        conn.tts.tts_text_queue.put(
            TTSMessageDTO(
                sentence_id=sentence_id,
                sentence_type=SentenceType.LAST,
                content_type=ContentType.ACTION,
            )
        )
        conn.tts_MessageText = text
        return self._json_response({"status": "ok", "sentence_id": sentence_id})
