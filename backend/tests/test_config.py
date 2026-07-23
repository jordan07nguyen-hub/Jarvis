from __future__ import annotations

from jarvis_backend.core.config import PROVIDER_PRIORITY, Settings


def test_default_provider_priority_matches_spec():
    settings = Settings(anthropic_api_key=None)
    assert settings.provider_priority == PROVIDER_PRIORITY
    assert settings.provider_priority[0] == "claude"


def test_pinning_a_provider_moves_it_first():
    settings = Settings(ai_provider="ollama")
    assert settings.provider_priority[0] == "ollama"
    assert set(settings.provider_priority) == set(PROVIDER_PRIORITY)
