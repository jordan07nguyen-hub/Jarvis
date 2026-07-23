"""Central configuration for the JARVIS backend.

Everything environment- or secret-specific lives here, read from the
process environment / a `.env` file — never hard-coded and never committed.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

ProviderName = Literal["claude", "openai", "ollama", "gemini", "openrouter"]

# First configured provider in this order wins, unless `ai_provider` pins one.
PROVIDER_PRIORITY: tuple[ProviderName, ...] = (
    "claude",
    "openai",
    "ollama",
    "gemini",
    "openrouter",
)

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="JARVIS_", extra="ignore")

    app_name: str = "JARVIS"
    # Loopback-only by default — this is a single-user local assistant, not a
    # service meant to be reachable from other devices. Opting into a wider
    # bind address is a deliberate choice the user makes, not the default.
    host: str = "127.0.0.1"
    port: int = 8000

    # Bearer token required on /api/chat and /ws/chat. Leave unset to have one
    # generated and persisted on first run (see core/auth.py) — set explicitly
    # to pin it (e.g. for the macOS app to read from Keychain/config).
    api_token: str | None = None

    # Origins allowed to make cross-origin browser requests to the REST API.
    # Empty by default: this backend is talked to by the native macOS app
    # (which isn't a browser and isn't subject to CORS), not by web pages.
    cors_allow_origins: list[str] = []

    # Pin a specific provider, or leave None to auto-select by priority.
    ai_provider: ProviderName | None = None

    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-5"
    # Lets Claude search the web for news/current facts via Anthropic's
    # server-side web_search tool — no separate search API key needed.
    anthropic_web_search: bool = True

    openai_api_key: str | None = None
    openai_model: str = "gpt-4o"

    # None until explicitly set — an always-present default would make Ollama
    # look "configured" even when no local daemon is running.
    ollama_base_url: str | None = None
    ollama_model: str = "llama3.1"

    gemini_api_key: str | None = None
    gemini_model: str = "gemini-1.5-pro"

    openrouter_api_key: str | None = None
    openrouter_model: str = "anthropic/claude-3.5-sonnet"

    memory_db_path: Path = DATA_DIR / "memory.sqlite3"

    @property
    def provider_priority(self) -> tuple[ProviderName, ...]:
        if self.ai_provider:
            rest = tuple(p for p in PROVIDER_PRIORITY if p != self.ai_provider)
            return (self.ai_provider, *rest)
        return PROVIDER_PRIORITY


@lru_cache
def get_settings() -> Settings:
    return Settings()
