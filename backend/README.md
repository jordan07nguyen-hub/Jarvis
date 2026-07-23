# JARVIS backend

FastAPI service that powers the JARVIS macOS app: chat (REST + streaming
WebSocket), a multi-provider AI abstraction, memory, and a plugin/tool
system. See [../ARCHITECTURE.md](../ARCHITECTURE.md) for the overall design
and [../ROADMAP.md](../ROADMAP.md) for what's implemented versus planned.

## Setup

Requires Python 3.11+ and [Poetry](https://python-poetry.org/).

```bash
cd backend
poetry install
cp .env.example .env   # fill in at least one provider's API key
poetry run python -m jarvis_backend.main
```

The server starts on `http://localhost:8000` (loopback-only by default —
see Security below). Interactive API docs at `/docs`.

Want it running automatically at login instead of a terminal window?
See [`apps/macos/launchd/`](../apps/macos/launchd/) for a macOS LaunchAgent.

On first run it prints a generated API token to the console and saves it
to `data/api_token.txt` — you need this to call the API.

## Configuration

All config is environment-driven (`JARVIS_*` variables, loaded from
`.env`) — see `.env.example` for the full list. The active AI provider is
chosen by priority (Claude → OpenAI → Ollama → Gemini → OpenRouter),
picking the first one with credentials configured, or pin one explicitly
with `JARVIS_AI_PROVIDER`.

When Claude is the active provider, JARVIS can search the web for news
and current facts via Anthropic's server-side `web_search` tool — no
separate search API key required. On by default; disable with
`JARVIS_ANTHROPIC_WEB_SEARCH=false`.

## Security

This is a single-user local assistant, not a multi-tenant service, but it
still needs basic guardrails since anything listening on a port is
reachable by other local processes/devices unless you lock it down:

- Binds to `127.0.0.1` by default (not `0.0.0.0`) — only reachable from
  your own machine unless you deliberately widen `JARVIS_HOST`.
- Every request to `/api/chat` and `/ws/chat` requires the bearer token
  (`Authorization: Bearer <token>` header, or `?token=...` for the
  WebSocket if your client can't set handshake headers). Get the token
  from the console output / `data/api_token.txt` on first run, or pin one
  yourself via `JARVIS_API_TOKEN`.
- No browser origin is trusted: `/ws/chat` rejects any handshake carrying
  an `Origin` header, and the REST API only allows cross-origin browser
  calls from origins you explicitly list in `JARVIS_CORS_ALLOW_ORIGINS`
  (empty/denied by default).
- Provider errors are logged server-side, not forwarded to clients — a
  failed request gets a generic error message, never the raw exception
  (which, e.g. for a misbehaving provider, could otherwise leak
  credentials embedded in a request URL).

## Endpoints

All routes below require the bearer token described above.

- `GET /health` — liveness check (no token required).
- `POST /api/chat` — single-turn chat: `{"session_id": "...", "message": "..."}`.
- `WS /ws/chat` — streaming chat. Send `{"session_id": "...", "message": "..."}`
  as JSON; receive a stream of `{"type": "chunk", "text": "..."}` frames
  followed by `{"type": "done"}` (or `{"type": "error", "message": "..."}`).

## Adding a provider

Implement `AIProvider` (`jarvis_backend/providers/base.py`), register it in
`_PROVIDER_CLASSES` in `providers/registry.py`, and add it to
`PROVIDER_PRIORITY` in `core/config.py`. Nothing else needs to change.

## Adding a plugin (tool)

Drop a module under `jarvis_backend/plugins/installed/` with a class that
subclasses `Plugin` (`jarvis_backend/plugins/base.py`) and implements
`run()`. It's auto-discovered on startup — see `plugins/installed/system_info.py`
for the pattern.

## Testing

```bash
poetry run pytest
poetry run ruff check jarvis_backend tests
```

## Docker

```bash
docker build -t jarvis-backend .
docker run -p 8000:8000 --env-file .env jarvis-backend
```
