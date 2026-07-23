"""Local Ollama provider — used for offline mode."""
from __future__ import annotations

from collections.abc import AsyncIterator

import httpx

from jarvis_backend.core.config import Settings
from jarvis_backend.providers.base import AIProvider, ChatMessage


class OllamaProvider(AIProvider):
    name = "ollama"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def is_configured(self) -> bool:
        # Configured means "worth trying" — actual reachability is checked at call time,
        # since a local daemon may not be running.
        return bool(self._settings.ollama_base_url)

    async def _is_reachable(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=2) as client:
                resp = await client.get(f"{self._settings.ollama_base_url}/api/tags")
                return resp.status_code == 200
        except httpx.HTTPError:
            return False

    async def chat(self, messages: list[ChatMessage]) -> str:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self._settings.ollama_base_url}/api/chat",
                json={
                    "model": self._settings.ollama_model,
                    "messages": [{"role": m.role, "content": m.content} for m in messages],
                    "stream": False,
                },
            )
            resp.raise_for_status()
            return resp.json()["message"]["content"]

    async def stream_chat(self, messages: list[ChatMessage]) -> AsyncIterator[str]:
        async with httpx.AsyncClient(timeout=120) as client, client.stream(
            "POST",
            f"{self._settings.ollama_base_url}/api/chat",
            json={
                "model": self._settings.ollama_model,
                "messages": [{"role": m.role, "content": m.content} for m in messages],
                "stream": True,
            },
        ) as resp:
            async for line in resp.aiter_lines():
                if not line:
                    continue
                import json

                chunk = json.loads(line)
                if content := chunk.get("message", {}).get("content"):
                    yield content
