from __future__ import annotations

import pytest

from jarvis_backend.core.config import Settings
from jarvis_backend.providers.base import ProviderNotConfiguredError
from jarvis_backend.providers.registry import ProviderRegistry


def test_no_providers_configured_raises(settings: Settings):
    registry = ProviderRegistry(settings)
    with pytest.raises(ProviderNotConfiguredError):
        registry.active()


def test_claude_selected_when_configured(settings: Settings):
    settings = settings.model_copy(update={"anthropic_api_key": "sk-test"})
    registry = ProviderRegistry(settings)
    assert registry.active().name == "claude"


def test_falls_back_to_next_configured_provider(settings: Settings):
    settings = settings.model_copy(update={"openai_api_key": "sk-test"})
    registry = ProviderRegistry(settings)
    assert registry.active().name == "openai"


def test_pinned_provider_wins_even_if_others_configured(settings: Settings):
    settings = settings.model_copy(
        update={
            "anthropic_api_key": "sk-test",
            "openai_api_key": "sk-test",
            "ai_provider": "openai",
        }
    )
    registry = ProviderRegistry(settings)
    assert registry.active().name == "openai"
