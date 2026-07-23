"""Example plugin: reports basic host system info.

Seed for the macOS system-control plugins tracked in ROADMAP.md Phase 7
(Finder, Safari, Notes, ...) — those follow this same shape, just calling
into macOS frameworks/AppleScript instead of `platform`.
"""
from __future__ import annotations

import platform
from typing import Any

from jarvis_backend.plugins.base import Plugin


class SystemInfoPlugin(Plugin):
    name = "system_info"
    description = "Report basic information about the host machine."

    async def run(self, args: dict[str, Any]) -> dict[str, Any]:
        return {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python_version": platform.python_version(),
        }
