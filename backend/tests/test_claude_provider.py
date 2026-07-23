from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from jarvis_backend.core.config import Settings
from jarvis_backend.providers.base import ChatMessage
from jarvis_backend.providers.claude import ClaudeProvider


def _text_response(text: str) -> MagicMock:
    block = MagicMock()
    block.type = "text"
    block.text = text
    response = MagicMock()
    response.content = [block]
    return response


@pytest.mark.asyncio
async def test_web_search_tool_included_by_default():
    settings = Settings(anthropic_api_key="sk-test")
    provider = ClaudeProvider(settings)
    provider._client.messages.create = AsyncMock(return_value=_text_response("hi"))

    await provider.chat([ChatMessage(role="user", content="what's the news today?")])

    _, kwargs = provider._client.messages.create.call_args
    assert kwargs["tools"] == [{"type": "web_search_20260209", "name": "web_search"}]


@pytest.mark.asyncio
async def test_web_search_tool_omitted_when_disabled():
    settings = Settings(anthropic_api_key="sk-test", anthropic_web_search=False)
    provider = ClaudeProvider(settings)
    provider._client.messages.create = AsyncMock(return_value=_text_response("hi"))

    await provider.chat([ChatMessage(role="user", content="hello")])

    _, kwargs = provider._client.messages.create.call_args
    assert kwargs["tools"] == []
