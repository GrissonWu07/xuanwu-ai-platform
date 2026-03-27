from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.connection import ConnectionHandler


class LocalFallbackDialogueEngine:
    async def run_turn(self, conn: "ConnectionHandler", user_text: str) -> None:
        conn.executor.submit(conn.chat, user_text)

    async def abort_turn(self, conn: "ConnectionHandler") -> None:
        return None