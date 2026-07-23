"""Google Gemini provider."""
from __future__ import annotations

from collections.abc import AsyncIterator

import httpx

from jarvis_backend.core.config import Settings
from jarvis_backend.providers.base import AIProvider, ChatMessage


class GeminiProvider(AIProvider):
    name = "gemini"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def is_configured(self) -> bool:
        return bool(self._settings.gemini_api_key)

    def _url(self) -> str:
        model = self._settings.gemini_model
        return f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    async def chat(self, messages: list[ChatMessage]) -> str:
        if not self.is_configured():
            raise RuntimeError("Gemini provider is not configured")
        contents = [
            {"role": "model" if m.role == "assistant" else "user", "parts": [{"text": m.content}]}
            for m in messages
            if m.role != "system"
        ]
        async with httpx.AsyncClient(timeout=60) as client:
            # Key goes in a header, not the URL — the URL ends up in exception
            # messages/logs on failure, a header does not.
            resp = await client.post(
                self._url(),
                headers={"x-goog-api-key": self._settings.gemini_api_key},
                json={"contents": contents},
            )
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

    async def stream_chat(self, messages: list[ChatMessage]) -> AsyncIterator[str]:
        yield await self.chat(messages)
