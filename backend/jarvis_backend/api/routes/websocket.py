"""Streaming chat over WebSocket — what the macOS app connects to.

Protocol: client sends {"session_id": str, "message": str} as JSON text
frames; server streams back {"type": "chunk", "text": str} frames followed
by a final {"type": "done"} frame. Any error becomes {"type": "error", ...}.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from jarvis_backend.api.deps import get_provider_registry, get_short_term_memory
from jarvis_backend.memory.short_term import ShortTermMemory
from jarvis_backend.providers.base import ChatMessage
from jarvis_backend.providers.registry import ProviderRegistry

router = APIRouter()


@router.websocket("/ws/chat")
async def chat_ws(
    websocket: WebSocket,
    providers: ProviderRegistry = Depends(get_provider_registry),
    memory: ShortTermMemory = Depends(get_short_term_memory),
) -> None:
    await websocket.accept()
    try:
        while True:
            payload = await websocket.receive_json()
            session_id = payload.get("session_id", "default")
            message = payload["message"]

            memory.append(session_id, ChatMessage(role="user", content=message))

            try:
                provider = providers.active()
                full_reply = ""
                async for chunk in provider.stream_chat(memory.history(session_id)):
                    full_reply += chunk
                    await websocket.send_json({"type": "chunk", "text": chunk})
                memory.append(session_id, ChatMessage(role="assistant", content=full_reply))
                await websocket.send_json({"type": "done"})
            except Exception as exc:  # noqa: BLE001 — surface any provider failure to the client
                await websocket.send_json({"type": "error", "message": str(exc)})
    except WebSocketDisconnect:
        pass
