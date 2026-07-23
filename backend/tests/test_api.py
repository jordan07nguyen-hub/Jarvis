from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from jarvis_backend.api.deps import get_provider_registry, get_short_term_memory
from jarvis_backend.core.auth import get_api_token
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


def _auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {get_api_token()}"}


def test_health():
    client = _client()
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_chat_endpoint_requires_token():
    client = _client()
    resp = client.post("/api/chat", json={"session_id": "s0", "message": "hello"})
    assert resp.status_code == 401


def test_chat_endpoint_rejects_wrong_token():
    client = _client()
    resp = client.post(
        "/api/chat",
        json={"session_id": "s0", "message": "hello"},
        headers={"Authorization": "Bearer not-the-real-token"},
    )
    assert resp.status_code == 401


def test_chat_endpoint_uses_active_provider():
    client = _client()
    resp = client.post(
        "/api/chat", json={"session_id": "s1", "message": "hello"}, headers=_auth_headers()
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["provider"] == "stub"
    assert body["reply"] == "echo: hello"


def test_chat_endpoint_remembers_session_history():
    client = _client()
    client.post(
        "/api/chat", json={"session_id": "s2", "message": "first"}, headers=_auth_headers()
    )
    resp = client.post(
        "/api/chat", json={"session_id": "s2", "message": "second"}, headers=_auth_headers()
    )
    assert resp.json()["reply"] == "echo: second"


def test_websocket_requires_token():
    client = _client()
    try:
        with client.websocket_connect("/ws/chat"):
            raise AssertionError("expected the handshake to be rejected")
    except WebSocketDisconnect as exc:
        assert exc.code == 1008


def test_websocket_rejects_browser_origin_even_with_valid_token():
    client = _client()
    try:
        with client.websocket_connect(
            "/ws/chat",
            headers={
                "authorization": f"Bearer {get_api_token()}",
                "origin": "https://evil.example",
            },
        ):
            raise AssertionError("expected the handshake to be rejected")
    except WebSocketDisconnect as exc:
        assert exc.code == 1008


def test_websocket_streams_chunks_then_done():
    client = _client()
    with client.websocket_connect(
        "/ws/chat", headers={"authorization": f"Bearer {get_api_token()}"}
    ) as ws:
        ws.send_json({"session_id": "w1", "message": "hello there"})
        chunks = []
        while True:
            frame = ws.receive_json()
            if frame["type"] == "done":
                break
            assert frame["type"] == "chunk"
            chunks.append(frame["text"])
        assert "".join(chunks) == "echo: hello there "


def test_websocket_accepts_token_via_query_param():
    client = _client()
    with client.websocket_connect(f"/ws/chat?token={get_api_token()}") as ws:
        ws.send_json({"session_id": "w2", "message": "hi"})
        frame = ws.receive_json()
        assert frame["type"] == "chunk"
