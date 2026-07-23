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

The server starts on `http://localhost:8000`. Interactive API docs at
`/docs`.

## Configuration

All config is environment-driven (`JARVIS_*` variables, loaded from
`.env`) — see `.env.example` for the full list. The active AI provider is
chosen by priority (Claude → OpenAI → Ollama → Gemini → OpenRouter),
picking the first one with credentials configured, or pin one explicitly
with `JARVIS_AI_PROVIDER`.

## Endpoints

- `GET /health` — liveness check.
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
