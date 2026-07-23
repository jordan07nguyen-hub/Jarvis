from __future__ import annotations

import pytest

from jarvis_backend.plugins.loader import load_plugins


@pytest.mark.asyncio
async def test_system_info_plugin_is_discovered_and_runs():
    registry = load_plugins()
    plugin = registry.get("system_info")
    assert plugin is not None
    result = await plugin.run({})
    assert "system" in result
    assert "python_version" in result


def test_all_returns_registered_plugins():
    registry = load_plugins()
    names = [p.name for p in registry.all()]
    assert "system_info" in names
