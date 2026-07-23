from __future__ import annotations

from jarvis_backend.memory.long_term import LongTermMemory
from jarvis_backend.memory.project import ProjectMemory
from jarvis_backend.memory.short_term import ShortTermMemory
from jarvis_backend.providers.base import ChatMessage


def test_short_term_memory_tracks_per_session():
    memory = ShortTermMemory(max_turns=3)
    memory.append("a", ChatMessage(role="user", content="hi"))
    memory.append("b", ChatMessage(role="user", content="yo"))
    assert [m.content for m in memory.history("a")] == ["hi"]
    assert [m.content for m in memory.history("b")] == ["yo"]


def test_short_term_memory_respects_max_turns():
    memory = ShortTermMemory(max_turns=2)
    for i in range(5):
        memory.append("a", ChatMessage(role="user", content=str(i)))
    assert [m.content for m in memory.history("a")] == ["3", "4"]


def test_long_term_memory_remember_and_search(tmp_path):
    memory = LongTermMemory(tmp_path / "mem.sqlite3")
    memory.remember("favorite_editor", "VS Code")
    memory.remember("favorite_language", "Python")
    results = memory.search("favorite_editor")
    assert len(results) == 1
    assert results[0].value == "VS Code"
    memory.close()


def test_long_term_memory_forget(tmp_path):
    memory = LongTermMemory(tmp_path / "mem.sqlite3")
    fact = memory.remember("key", "value")
    memory.forget(fact.id)
    assert memory.search("key") == []
    memory.close()


def test_project_memory_scopes_notes_by_project(tmp_path):
    memory = ProjectMemory(tmp_path / "proj.sqlite3")
    memory.add_note("jarvis", "uses FastAPI")
    memory.add_note("other-project", "uses Django")
    notes = memory.notes_for("jarvis")
    assert len(notes) == 1
    assert notes[0].note == "uses FastAPI"
    memory.close()
