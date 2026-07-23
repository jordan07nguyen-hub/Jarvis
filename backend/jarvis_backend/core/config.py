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
    host: str = "0.0.0.0"
    port: int = 8000

    # Pin a specific provider, or leave None to auto-select by priority.
    ai_provider: ProviderName | None = None

    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-4-5-20250929"

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
