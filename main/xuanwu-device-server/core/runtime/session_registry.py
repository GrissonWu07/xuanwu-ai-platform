from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Any


@dataclass
class RuntimeSessionRecord:
    runtime_session_id: str
    device_id: str
    client_id: str | None
    atlas_session_key: str
    conn: Any


class RuntimeSessionRegistry:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._by_runtime_session: dict[str, RuntimeSessionRecord] = {}
        self._by_atlas_session: dict[str, str] = {}

    def register(
        self,
        runtime_session_id: str,
        *,
        device_id: str,
        client_id: str | None,
        atlas_session_key: str,
        conn: Any,
    ) -> RuntimeSessionRecord:
        record = RuntimeSessionRecord(
            runtime_session_id=runtime_session_id,
            device_id=device_id,
            client_id=client_id,
            atlas_session_key=atlas_session_key,
            conn=conn,
        )
        with self._lock:
            self._by_runtime_session[runtime_session_id] = record
            self._by_atlas_session[atlas_session_key] = runtime_session_id
        return record

    def unregister(self, runtime_session_id: str) -> None:
        with self._lock:
            record = self._by_runtime_session.pop(runtime_session_id, None)
            if record is not None:
                self._by_atlas_session.pop(record.atlas_session_key, None)

    def get_by_runtime_session(self, runtime_session_id: str) -> RuntimeSessionRecord | None:
        with self._lock:
            return self._by_runtime_session.get(runtime_session_id)

    def get_by_atlas_session(self, atlas_session_key: str) -> RuntimeSessionRecord | None:
        with self._lock:
            runtime_session_id = self._by_atlas_session.get(atlas_session_key)
            if runtime_session_id is None:
                return None
            return self._by_runtime_session.get(runtime_session_id)


runtime_session_registry = RuntimeSessionRegistry()
