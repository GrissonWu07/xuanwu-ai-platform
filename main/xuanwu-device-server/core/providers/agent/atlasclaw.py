from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING, Any, AsyncIterator

import aiohttp

from core.providers.agent.atlasclaw_stream_bridge import AtlasClawStreamBridge
from core.providers.agent.local_fallback import LocalFallbackDialogueEngine
from core.providers.agent.template_fallback import TemplateFallbackDialogueEngine
from core.utils.dialogue import Message

if TYPE_CHECKING:
    from core.connection import ConnectionHandler


class AtlasClawDialogueEngine:
    def __init__(self, config: dict, fallback=None):
        self.config = config
        self.agent_config = self._resolve_agent_config(config)
        self.fallback = fallback or self._build_fallback(config, self.agent_config)
        self.base_url = str(self.agent_config.get("base_url", "")).rstrip("/")
        self.timeout_seconds = int(self.agent_config.get("timeout_seconds", 120))
        self.api_key = str(self.agent_config.get("api_key", "")).strip()
        self._session: aiohttp.ClientSession | None = None

    @classmethod
    def from_config(cls, config: dict):
        agent_config = cls._resolve_agent_config(config)
        base_url = str(agent_config.get("base_url", "")).strip()
        if not base_url:
            return cls._build_fallback(config, agent_config)
        return cls(config)

    @staticmethod
    def _resolve_agent_config(config: dict) -> dict[str, Any]:
        selected_module = config.get("selected_module", {})
        agent_configs = config.get("Agent", {})
        selected_agent = selected_module.get("Agent")
        if selected_agent and isinstance(agent_configs.get(selected_agent), dict):
            return dict(agent_configs[selected_agent])
        if isinstance(agent_configs.get("AtlasClaw"), dict):
            return dict(agent_configs["AtlasClaw"])
        server_agent = config.get("server", {}).get("atlasclaw", {})
        if isinstance(server_agent, dict):
            return dict(server_agent)
        return {}

    @staticmethod
    def _build_fallback(config: dict, agent_config: dict[str, Any]):
        fallback_config = agent_config.get("fallback", {})
        if not isinstance(fallback_config, dict):
            fallback_config = {}
        mode = str(
            fallback_config.get("mode")
            or agent_config.get("fallback_mode")
            or "template"
        ).strip().lower()
        if mode == "local":
            return LocalFallbackDialogueEngine()
        reply_text = (
            fallback_config.get("message")
            or config.get("system_error_response")
            or "AtlasClaw is unavailable right now."
        )
        return TemplateFallbackDialogueEngine(reply_text)

    async def run_turn(self, conn: "ConnectionHandler", user_text: str) -> None:
        conn.client_abort = False
        await self.abort_turn(conn)
        conn.atlas_stream_task = asyncio.create_task(
            self._run_turn(conn, user_text),
            name=f"atlas-turn-{conn.runtime_session_id}",
        )

    async def abort_turn(self, conn: "ConnectionHandler") -> None:
        run_id = getattr(conn, "atlas_run_id", None)
        if run_id:
            try:
                session = await self._get_session()
                async with session.post(
                    f"{self.base_url}/agent/runs/{run_id}/abort",
                    headers=self._build_headers(),
                    timeout=aiohttp.ClientTimeout(total=5),
                ):
                    pass
            except Exception:
                conn.logger.bind(tag=__name__).warning(
                    f"Failed to abort AtlasClaw run: {run_id}",
                )

        task = getattr(conn, "atlas_stream_task", None)
        if task is not None and not task.done() and task is not asyncio.current_task():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            except Exception:
                pass

        conn.atlas_run_id = None
        conn.atlas_stream_task = None

    async def _run_turn(self, conn: "ConnectionHandler", user_text: str) -> None:
        bridge = AtlasClawStreamBridge(conn)
        conn.dialogue.put(Message(role="user", content=user_text))

        try:
            run_id = await self._start_run(conn, user_text)
            conn.atlas_run_id = run_id
            await self._consume_stream(conn, run_id, bridge)
            if not conn.client_abort:
                bridge.finish(empty_reply="Sorry, I do not have a spoken reply yet.")
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            conn.logger.bind(tag=__name__).error(f"AtlasClaw turn failed: {exc}")
            if bridge.has_output:
                bridge.finish()
            else:
                await self.fallback.run_turn(conn, user_text)
        finally:
            conn.atlas_run_id = None
            current_task = asyncio.current_task()
            if getattr(conn, "atlas_stream_task", None) is current_task:
                conn.atlas_stream_task = None

    async def _start_run(self, conn: "ConnectionHandler", user_text: str) -> str:
        payload = {
            "session_key": conn.atlas_session_key,
            "message": user_text,
            "timeout_seconds": self.timeout_seconds,
            "context": self._build_context(conn),
        }
        session = await self._get_session()
        async with session.post(
            f"{self.base_url}/agent/run",
            json=payload,
            headers=self._build_headers(),
            timeout=aiohttp.ClientTimeout(total=self.timeout_seconds),
        ) as response:
            response.raise_for_status()
            data = await response.json()
            run_id = str(data.get("run_id", "")).strip()
            if not run_id:
                raise RuntimeError("AtlasClaw did not return a run_id")
            return run_id

    async def _consume_stream(
        self,
        conn: "ConnectionHandler",
        run_id: str,
        bridge: AtlasClawStreamBridge,
    ) -> None:
        session = await self._get_session()
        async with session.get(
            f"{self.base_url}/agent/runs/{run_id}/stream",
            headers=self._build_stream_headers(),
            timeout=aiohttp.ClientTimeout(total=None, sock_read=None),
        ) as response:
            response.raise_for_status()
            async for event_type, payload in self._iter_sse_events(response):
                if conn.client_abort:
                    return
                if event_type == "assistant":
                    bridge.feed_text(str(payload.get("text", "")))
                elif event_type == "tool":
                    conn.logger.bind(tag=__name__).info(
                        f"AtlasClaw tool event: {payload}",
                    )
                elif event_type == "thinking":
                    continue
                elif event_type == "heartbeat":
                    continue
                elif event_type == "error":
                    bridge.fail(payload.get("message") or payload.get("error"))
                    return
                elif event_type == "lifecycle":
                    phase = str(payload.get("phase", "")).strip().lower()
                    if phase in {"end", "aborted", "error", "timeout"}:
                        return

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    def _build_headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _build_stream_headers(self) -> dict[str, str]:
        headers = {"Accept": "text/event-stream"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _build_context(self, conn: "ConnectionHandler") -> dict[str, Any]:
        headers = conn.headers or {}
        return {
            "device_id": conn.device_id,
            "client_id": headers.get("client-id"),
            "runtime_session_id": conn.runtime_session_id,
            "channel": "xuanwu",
            "bind_status": self._bind_status(conn),
            "locale": str(self.agent_config.get("locale") or conn.config.get("locale") or "zh-CN"),
            "audio_format": getattr(conn, "audio_format", "opus"),
            "capabilities": {
                "speaker": conn.tts is not None,
                "camera": self._has_tool(conn, "self_camera_take_photo"),
                "mcp": bool(getattr(conn, "features", None)) or hasattr(conn, "mcp_endpoint_client"),
                "iot": bool(getattr(conn, "iot_descriptors", {})),
            },
            "device_metadata": {
                "sample_rate": getattr(conn, "sample_rate", None),
                "firmware_version": headers.get("x-firmware-version") or headers.get("firmware-version"),
            },
        }

    def _bind_status(self, conn: "ConnectionHandler") -> str:
        if not conn.device_id:
            return "unknown"
        return "pending" if getattr(conn, "need_bind", False) else "bound"

    def _has_tool(self, conn: "ConnectionHandler", tool_name: str) -> bool:
        func_handler = getattr(conn, "func_handler", None)
        if not func_handler or not getattr(func_handler, "finish_init", False):
            return False
        try:
            return bool(func_handler.has_tool(tool_name))
        except Exception:
            return False

    async def _iter_sse_events(
        self,
        response: aiohttp.ClientResponse,
    ) -> AsyncIterator[tuple[str, dict[str, Any]]]:
        event_type = "message"
        data_lines: list[str] = []

        async for chunk in response.content:
            line = chunk.decode("utf-8").strip()
            if not line:
                if data_lines:
                    payload = self._decode_payload("\n".join(data_lines))
                    yield event_type, payload
                    event_type = "message"
                    data_lines = []
                continue
            if line.startswith(":"):
                continue
            if line.startswith("event:"):
                event_type = line[6:].strip()
                continue
            if line.startswith("data:"):
                data_lines.append(line[5:].strip())

        if data_lines:
            yield event_type, self._decode_payload("\n".join(data_lines))

    def _decode_payload(self, raw_data: str) -> dict[str, Any]:
        if not raw_data:
            return {}
        try:
            payload = json.loads(raw_data)
            return payload if isinstance(payload, dict) else {"value": payload}
        except json.JSONDecodeError:
            return {"message": raw_data}
