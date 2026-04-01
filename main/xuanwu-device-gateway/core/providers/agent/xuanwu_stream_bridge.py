from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from core.providers.tts.dto.dto import ContentType, SentenceType, TTSMessageDTO
from core.utils.dialogue import Message

if TYPE_CHECKING:
    from core.connection import ConnectionHandler


class XuanWuStreamBridge:
    HARD_BOUNDARIES = set("。！？!?.;；\n")
    SOFT_BOUNDARIES = set("，,")

    def __init__(self, conn: "ConnectionHandler") -> None:
        self.conn = conn
        self.buffer = ""
        self.full_text = ""
        self.started = False
        self.finished = False
        self.sentence_id = str(uuid.uuid4().hex)
        self.conn.sentence_id = self.sentence_id

    @property
    def has_output(self) -> bool:
        return bool(self.full_text.strip())

    def feed_text(self, text: str) -> None:
        if not text or self.conn.client_abort:
            return
        self._ensure_started()
        self.buffer += text
        self.full_text += text
        for segment in self._pop_ready_segments(final=False):
            self.conn.tts.tts_one_sentence(
                self.conn,
                ContentType.TEXT,
                content_detail=segment,
            )
        self.conn.tts_MessageText = self.full_text

    def finish(self, *, empty_reply: str | None = None) -> None:
        if self.finished or self.conn.client_abort:
            return
        if not self.started and empty_reply:
            self.feed_text(empty_reply)
        elif empty_reply and not self.has_output:
            self.feed_text(empty_reply)

        for segment in self._pop_ready_segments(final=True):
            self.conn.tts.tts_one_sentence(
                self.conn,
                ContentType.TEXT,
                content_detail=segment,
            )

        if self.started:
            self.conn.tts.tts_text_queue.put(
                TTSMessageDTO(
                    sentence_id=self.sentence_id,
                    sentence_type=SentenceType.LAST,
                    content_type=ContentType.ACTION,
                )
            )

        if self.has_output:
            self.conn.dialogue.put(Message(role="assistant", content=self.full_text))
            self.conn.tts_MessageText = self.full_text

        self.finished = True

    def fail(self, message: str | None = None) -> None:
        if self.conn.client_abort:
            return
        self.finish(empty_reply=message or "抱歉，我暂时无法处理这个请求。")

    def _ensure_started(self) -> None:
        if self.started:
            return
        self.conn.tts.tts_text_queue.put(
            TTSMessageDTO(
                sentence_id=self.sentence_id,
                sentence_type=SentenceType.FIRST,
                content_type=ContentType.ACTION,
            )
        )
        self.started = True

    def _pop_ready_segments(self, *, final: bool) -> list[str]:
        segments: list[str] = []
        while self.buffer:
            split_index = self._find_split_index(final=final)
            if split_index is None:
                break
            segment = self.buffer[:split_index].strip()
            self.buffer = self.buffer[split_index:].lstrip()
            if segment:
                segments.append(segment)
        return segments

    def _find_split_index(self, *, final: bool) -> int | None:
        for index, char in enumerate(self.buffer):
            if char in self.HARD_BOUNDARIES:
                return index + 1

        if len(self.buffer) >= 80:
            for index, char in enumerate(self.buffer):
                if char in self.SOFT_BOUNDARIES:
                    return index + 1

        if final and self.buffer.strip():
            return len(self.buffer)

        if len(self.buffer) >= 160:
            return 160

        return None
