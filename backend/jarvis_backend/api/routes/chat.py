"""REST chat endpoint: single request/response turn.

For streaming/conversational use (what the macOS app uses), see
`api/routes/websocket.py`.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from jarvis_backend.api.deps import get_provider_registry, get_short_term_memory
from jarvis_backend.core.auth import require_token
from jarvis_backend.memory.short_term import ShortTermMemory
from jarvis_backend.providers.base import ChatMessage
from jarvis_backend.providers.registry import ProviderRegistry

router = APIRouter(dependencies=[Depends(require_token)])
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    session_id: str = "default"
    message: str


class ChatResponse(BaseModel):
    session_id: str
    provider: str
    reply: str


@router.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    providers: ProviderRegistry = Depends(get_provider_registry),
    memory: ShortTermMemory = Depends(get_short_term_memory),
) -> ChatResponse:
    memory.append(request.session_id, ChatMessage(role="user", content=request.message))
    provider = providers.active()
    try:
        reply = await provider.chat(memory.history(request.session_id))
    except Exception:
        logger.exception("Provider %s failed to answer chat request", provider.name)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail="AI provider request failed"
        ) from None
    memory.append(request.session_id, ChatMessage(role="assistant", content=reply))
    return ChatResponse(session_id=request.session_id, provider=provider.name, reply=reply)
