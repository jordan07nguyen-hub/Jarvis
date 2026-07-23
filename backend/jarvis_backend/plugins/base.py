"""Plugin (tool) interface.

A plugin is a single callable capability JARVIS can invoke — a macOS system
action, a GitHub operation, a web search, etc. Each one lives in its own
module under `plugins/installed/` and is auto-discovered by `PluginLoader`.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Plugin(ABC):
    name: str
    description: str

    @abstractmethod
    async def run(self, args: dict[str, Any]) -> dict[str, Any]:
        """Execute the plugin's action and return a JSON-serializable result."""
