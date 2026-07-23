"""Per-project notes/context store, backed by SQLite.

Separate from LongTermMemory because project context has a different
lifetime and query shape: it's scoped to a project name, not searched
globally.
"""
from __future__ import annotations

import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectNote:
    id: int
    project: str
    note: str
    created_at: float


class ProjectMemory:
    def __init__(self, db_path: Path) -> None:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS project_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project TEXT NOT NULL,
                note TEXT NOT NULL,
                created_at REAL NOT NULL
            )
            """
        )
        self._conn.commit()

    def add_note(self, project: str, note: str) -> ProjectNote:
        now = time.time()
        cur = self._conn.execute(
            "INSERT INTO project_notes (project, note, created_at) VALUES (?, ?, ?)",
            (project, note, now),
        )
        self._conn.commit()
        return ProjectNote(id=cur.lastrowid, project=project, note=note, created_at=now)

    def notes_for(self, project: str, limit: int = 50) -> list[ProjectNote]:
        rows = self._conn.execute(
            "SELECT id, project, note, created_at FROM project_notes "
            "WHERE project = ? ORDER BY created_at DESC LIMIT ?",
            (project, limit),
        ).fetchall()
        return [ProjectNote(*row) for row in rows]

    def close(self) -> None:
        self._conn.close()
