from __future__ import annotations

import pytest

from jarvis_backend.core.config import Settings


@pytest.fixture
def settings(tmp_path) -> Settings:
    return Settings(memory_db_path=tmp_path / "memory.sqlite3")
