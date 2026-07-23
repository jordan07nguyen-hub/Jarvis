"""Discovers and registers Plugin subclasses under plugins/installed/."""
from __future__ import annotations

import importlib
import pkgutil

from jarvis_backend.plugins import installed
from jarvis_backend.plugins.base import Plugin


class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: dict[str, Plugin] = {}

    def register(self, plugin: Plugin) -> None:
        self._plugins[plugin.name] = plugin

    def get(self, name: str) -> Plugin | None:
        return self._plugins.get(name)

    def all(self) -> list[Plugin]:
        return list(self._plugins.values())


def load_plugins() -> PluginRegistry:
    registry = PluginRegistry()
    for module_info in pkgutil.iter_modules(installed.__path__, prefix=f"{installed.__name__}."):
        module = importlib.import_module(module_info.name)
        for attr in vars(module).values():
            if isinstance(attr, type) and issubclass(attr, Plugin) and attr is not Plugin:
                registry.register(attr())
    return registry
