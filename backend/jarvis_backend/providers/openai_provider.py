"""OpenAI provider, via plain HTTP so we don't need the full openai SDK."""
from __future__ import annotations

from collections.abc import AsyncIterator

import httpx

from jarvis_backend.core.config import Settings
from jarvis_backend.providers.base import AIProvider, ChatMessage

API_URL = "https://api.openai.com/v1/chat/completions"


class OpenAIProvider(AIProvider):
    name = "openai"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def is_configured(self) -> bool:
        return bool(self._settings.openai_api_key)

    async def chat(self, messages: list[ChatMessage]) -> str:
        if not self.is_configured():
            raise RuntimeError("OpenAI provider is not configured")
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                API_URL,
                headers={"Authorization": f"Bearer {self._settings.openai_api_key}"},
                json={
                    "model": self._settings.openai_model,
                    "messages": [{"role": m.role, "content": m.content} for m in messages],
                },
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]

    async def stream_chat(self, messages: list[ChatMessage]) -> AsyncIterator[str]:
        # MVP: no incremental streaming yet, yield the full response once.
        yield await self.chat(messages)
