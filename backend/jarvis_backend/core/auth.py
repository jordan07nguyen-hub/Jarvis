"""Local API token: authenticates the macOS app (or any client) to the backend.

This is a single-user local assistant, not a multi-tenant service — a
persisted random bearer token (same idea as Jupyter's default auth) is
enough to stop other processes/devices/browser tabs from silently using
the user's configured AI provider through their backend, without requiring
a full user-account system.
"""
from __future__ import annotations

import secrets
from functools import lru_cache
from pathlib import Path

from fastapi import Header, HTTPException, WebSocket, WebSocketException, status

from jarvis_backend.core.config import DATA_DIR, Settings, get_settings

TOKEN_FILE = DATA_DIR / "api_token.txt"


def _generate_and_persist_token(path: Path) -> str:
    token = secrets.token_urlsafe(32)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(token)
    return token


@lru_cache
def get_api_token() -> str:
    """Returns the configured token, or generates+persists one on first run."""
    settings: Settings = get_settings()
    if settings.api_token:
        return settings.api_token
    if TOKEN_FILE.exists():
        return TOKEN_FILE.read_text().strip()
    token = _generate_and_persist_token(TOKEN_FILE)
    print(  # noqa: T201 — this is the only way the user learns the token on first run
        f"\n[jarvis] Generated a new API token (saved to {TOKEN_FILE}):\n"
        f"[jarvis]   {token}\n"
        f"[jarvis] Configure the macOS app with this token, or set JARVIS_API_TOKEN "
        f"to pin your own.\n"
    )
    return token


def _matches(provided: str | None) -> bool:
    return bool(provided) and secrets.compare_digest(provided, get_api_token())


async def require_token(authorization: str | None = Header(default=None)) -> None:
    """FastAPI dependency for REST routes: expects `Authorization: Bearer <token>`."""
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:]
    if not _matches(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token")


async def require_websocket_auth(websocket: WebSocket) -> None:
    """FastAPI dependency for the WebSocket route: token + no browser Origin.

    No legitimate caller of this endpoint is a browser page, so any
    handshake carrying an `Origin` header (which only browsers send) is
    rejected outright, on top of the same bearer token REST requires —
    from a header, or `?token=...` for clients that can't set handshake
    headers.
    """
    if websocket.headers.get("origin") is not None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    header = websocket.headers.get("authorization")
    token = None
    if header and header.lower().startswith("bearer "):
        token = header[7:]
    if not token:
        token = websocket.query_params.get("token")
    if not _matches(token):
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
