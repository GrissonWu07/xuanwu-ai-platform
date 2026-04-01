from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from core.connection import ConnectionHandler


class DialogueEngine(Protocol):
    async def run_turn(self, conn: "ConnectionHandler", user_text: str) -> None: ...

    async def abort_turn(self, conn: "ConnectionHandler") -> None: ...