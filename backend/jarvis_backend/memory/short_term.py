"""In-process rolling conversation buffer, scoped per session.

This is intentionally not durable — it's the assistant's working memory for
the current conversation. Durable facts belong in LongTermMemory.
"""
from __future__ import annotations

from collections import defaultdict, deque

from jarvis_backend.providers.base import ChatMessage


class ShortTermMemory:
    def __init__(self, max_turns: int = 40) -> None:
        self._max_turns = max_turns
        self._sessions: dict[str, deque[ChatMessage]] = defaultdict(
            lambda: deque(maxlen=max_turns)
        )

    def append(self, session_id: str, message: ChatMessage) -> None:
        self._sessions[session_id].append(message)

    def history(self, session_id: str) -> list[ChatMessage]:
        return list(self._sessions[session_id])

    def clear(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)
