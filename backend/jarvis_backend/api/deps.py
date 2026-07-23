"""Shared FastAPI dependencies: singletons for settings, memory, providers, plugins."""
from __future__ import annotations

from functools import lru_cache

from jarvis_backend.core.config import Settings, get_settings
from jarvis_backend.memory.long_term import LongTermMemory
from jarvis_backend.memory.project import ProjectMemory
from jarvis_backend.memory.short_term import ShortTermMemory
from jarvis_backend.plugins.loader import PluginRegistry, load_plugins
from jarvis_backend.providers.registry import ProviderRegistry


@lru_cache
def get_provider_registry() -> ProviderRegistry:
    return ProviderRegistry(get_settings())


@lru_cache
def get_short_term_memory() -> ShortTermMemory:
    return ShortTermMemory()


@lru_cache
def get_long_term_memory() -> LongTermMemory:
    settings: Settings = get_settings()
    return LongTermMemory(settings.memory_db_path)


@lru_cache
def get_project_memory() -> ProjectMemory:
    settings: Settings = get_settings()
    return ProjectMemory(settings.memory_db_path.with_name("projects.sqlite3"))


@lru_cache
def get_plugin_registry() -> PluginRegistry:
    return load_plugins()
