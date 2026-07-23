from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi.testclient import TestClient

from jarvis_backend.api.deps import get_provider_registry, get_short_term_memory
from jarvis_backend.main import app
from jarvis_backend.memory.short_term import ShortTermMemory
from jarvis_backend.providers.base import AIProvider, ChatMessage


class StubProvider(AIProvider):
    name = "stub"

    def is_configured(self) -> bool:
        return True

    async def chat(self, messages: list[ChatMessage]) -> str:
        return f"echo: {messages[-1].content}"

    async def stream_chat(self, messages: list[ChatMessage]) -> AsyncIterator[str]:
        for word in f"echo: {messages[-1].content}".split(" "):
            yield word + " "


class StubRegistry:
    def active(self) -> AIProvider:
        return StubProvider()


def _client() -> TestClient:
    app.dependency_overrides[get_provider_registry] = lambda: StubRegistry()
    app.dependency_overrides[get_short_term_memory] = lambda: ShortTermMemory()
    return TestClient(app)


def test_health():
    client = _client()
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_chat_endpoint_uses_active_provider():
    client = _client()
    resp = client.post("/api/chat", json={"session_id": "s1", "message": "hello"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["provider"] == "stub"
    assert body["reply"] == "echo: hello"


def test_chat_endpoint_remembers_session_history():
    client = _client()
    client.post("/api/chat", json={"session_id": "s2", "message": "first"})
    resp = client.post("/api/chat", json={"session_id": "s2", "message": "second"})
    assert resp.json()["reply"] == "echo: second"


def test_websocket_streams_chunks_then_done():
    client = _client()
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json({"session_id": "w1", "message": "hello there"})
        chunks = []
        while True:
            frame = ws.receive_json()
            if frame["type"] == "done":
                break
            assert frame["type"] == "chunk"
            chunks.append(frame["text"])
        assert "".join(chunks) == "echo: hello there "
