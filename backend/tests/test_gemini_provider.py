from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from jarvis_backend.core.config import Settings
from jarvis_backend.providers.base import ChatMessage
from jarvis_backend.providers.gemini import GeminiProvider


@pytest.mark.asyncio
async def test_gemini_sends_key_as_header_not_in_url():
    settings = Settings(gemini_api_key="super-secret-key")
    provider = GeminiProvider(settings)

    mock_response = AsyncMock()
    mock_response.raise_for_status = lambda: None
    mock_response.json = lambda: {"candidates": [{"content": {"parts": [{"text": "hi"}]}}]}

    with patch("httpx.AsyncClient.post", new=AsyncMock(return_value=mock_response)) as mock_post:
        await provider.chat([ChatMessage(role="user", content="hello")])

    called_url = mock_post.call_args.args[0]
    called_headers = mock_post.call_args.kwargs["headers"]
    assert "super-secret-key" not in called_url
    assert called_headers["x-goog-api-key"] == "super-secret-key"
