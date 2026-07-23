"""Durable facts/preferences store, backed by SQLite.

Search today is a simple keyword LIKE query. The interface is deliberately
narrow (`remember` / `search` / `forget`) so a vector-embedding backend
(e.g. ChromaDB, see ROADMAP.md Phase 6) can replace the storage engine
later without touching callers.
"""
from __future__ import annotations

import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Fact:
    id: int
    key: str
    value: str
    created_at: float


class LongTermMemory:
    def __init__(self, db_path: Path) -> None:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                created_at REAL NOT NULL
            )
            """
        )
        self._conn.commit()

    def remember(self, key: str, value: str) -> Fact:
        now = time.time()
        cur = self._conn.execute(
            "INSERT INTO facts (key, value, created_at) VALUES (?, ?, ?)",
            (key, value, now),
        )
        self._conn.commit()
        return Fact(id=cur.lastrowid, key=key, value=value, created_at=now)

    def search(self, query: str, limit: int = 10) -> list[Fact]:
        rows = self._conn.execute(
            "SELECT id, key, value, created_at FROM facts "
            "WHERE key LIKE ? OR value LIKE ? ORDER BY created_at DESC LIMIT ?",
            (f"%{query}%", f"%{query}%", limit),
        ).fetchall()
        return [Fact(*row) for row in rows]

    def forget(self, fact_id: int) -> None:
        self._conn.execute("DELETE FROM facts WHERE id = ?", (fact_id,))
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()
