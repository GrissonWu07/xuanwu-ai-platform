from __future__ import annotations

from typing import TYPE_CHECKING

from core.providers.tts.dto.dto import ContentType
from core.utils.dialogue import Message

if TYPE_CHECKING:
    from core.connection import ConnectionHandler


class TemplateFallbackDialogueEngine:
    def __init__(self, reply_text: str):
        self.reply_text = str(reply_text or "").strip() or "Service unavailable."

    async def run_turn(self, conn: "ConnectionHandler", user_text: str) -> None:
        if getattr(conn, "tts", None) is not None:
            conn.tts.tts_one_sentence(conn, ContentType.TEXT, content_detail=self.reply_text)
        if getattr(conn, "dialogue", None) is not None:
            conn.dialogue.put(Message(role="assistant", content=self.reply_text))
        conn.tts_MessageText = self.reply_text

    async def abort_turn(self, conn: "ConnectionHandler") -> None:
        return None
