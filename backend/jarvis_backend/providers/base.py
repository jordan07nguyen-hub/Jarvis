"""Common interface every AI provider implements.

Adding a new provider means implementing this one class — nothing else in
the backend needs to change.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Literal

Role = Literal["system", "user", "assistant"]


@dataclass(frozen=True)
class ChatMessage:
    role: Role
    content: str


class AIProvider(ABC):
    """Base class for a chat-completion backend."""

    name: str

    @abstractmethod
    def is_configured(self) -> bool:
        """Whether this provider has what it needs (API key, reachable host, ...)."""

    @abstractmethod
    async def chat(self, messages: list[ChatMessage]) -> str:
        """Return a single complete response."""

    @abstractmethod
    async def stream_chat(self, messages: list[ChatMessage]) -> AsyncIterator[str]:
        """Yield the response incrementally, chunk by chunk."""


class ProviderNotConfiguredError(RuntimeError):
    """Raised when no AI provider in the priority list is usable."""
