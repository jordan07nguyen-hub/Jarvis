"""Resolves which configured AI provider to use, in priority order."""
from __future__ import annotations

from jarvis_backend.core.config import ProviderName, Settings
from jarvis_backend.providers.base import AIProvider, ProviderNotConfiguredError
from jarvis_backend.providers.claude import ClaudeProvider
from jarvis_backend.providers.gemini import GeminiProvider
from jarvis_backend.providers.ollama import OllamaProvider
from jarvis_backend.providers.openai_provider import OpenAIProvider
from jarvis_backend.providers.openrouter import OpenRouterProvider

_PROVIDER_CLASSES: dict[ProviderName, type[AIProvider]] = {
    "claude": ClaudeProvider,
    "openai": OpenAIProvider,
    "ollama": OllamaProvider,
    "gemini": GeminiProvider,
    "openrouter": OpenRouterProvider,
}


class ProviderRegistry:
    """Builds and selects providers according to `settings.provider_priority`."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._providers: dict[ProviderName, AIProvider] = {
            name: cls(settings) for name, cls in _PROVIDER_CLASSES.items()
        }

    def get(self, name: ProviderName) -> AIProvider:
        return self._providers[name]

    def active(self) -> AIProvider:
        for name in self._settings.provider_priority:
            provider = self._providers[name]
            if provider.is_configured():
                return provider
        raise ProviderNotConfiguredError(
            "No AI provider is configured. Set at least one API key "
            "(JARVIS_ANTHROPIC_API_KEY, JARVIS_OPENAI_API_KEY, ...) or run a local Ollama."
        )
