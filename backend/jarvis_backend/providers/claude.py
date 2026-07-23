"""Claude provider — the default, primary reasoning engine."""
from __future__ import annotations

from collections.abc import AsyncIterator

from anthropic import AsyncAnthropic

from jarvis_backend.core.config import Settings
from jarvis_backend.providers.base import AIProvider, ChatMessage


class ClaudeProvider(AIProvider):
    name = "claude"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: AsyncAnthropic | None = None
        if settings.anthropic_api_key:
            self._client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    def is_configured(self) -> bool:
        return self._client is not None

    def _split(self, messages: list[ChatMessage]) -> tuple[str | None, list[dict]]:
        system = next((m.content for m in messages if m.role == "system"), None)
        turns = [{"role": m.role, "content": m.content} for m in messages if m.role != "system"]
        return system, turns

    def _tools(self) -> list[dict]:
        if not self._settings.anthropic_web_search:
            return []
        # Server-side tool: Claude runs the search itself and cites results —
        # no separate search API key needed. Lets JARVIS answer "what's the
        # news on X" / current-facts questions instead of only training data.
        return [{"type": "web_search_20260209", "name": "web_search"}]

    async def chat(self, messages: list[ChatMessage]) -> str:
        if not self._client:
            raise RuntimeError("Claude provider is not configured")
        system, turns = self._split(messages)
        response = await self._client.messages.create(
            model=self._settings.anthropic_model,
            max_tokens=1024,
            system=system or "You are JARVIS, a helpful personal assistant.",
            messages=turns,
            tools=self._tools(),
        )
        return "".join(block.text for block in response.content if block.type == "text")

    async def stream_chat(self, messages: list[ChatMessage]) -> AsyncIterator[str]:
        if not self._client:
            raise RuntimeError("Claude provider is not configured")
        system, turns = self._split(messages)
        async with self._client.messages.stream(
            model=self._settings.anthropic_model,
            max_tokens=1024,
            system=system or "You are JARVIS, a helpful personal assistant.",
            messages=turns,
            tools=self._tools(),
        ) as stream:
            async for text in stream.text_stream:
                yield text
