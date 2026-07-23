# JARVIS Roadmap

Status legend: ✅ done (working + tested)  🚧 in progress this session  ⬜ planned, not started

| Phase | Scope | Status |
|-------|-------|--------|
| 1 | Architecture, folder structure, roadmap | ✅ |
| 2 | Backend: FastAPI app, config, provider abstraction (Claude/OpenAI/Ollama/Gemini/OpenRouter), REST + WebSocket chat, tested with pytest | 🚧 MVP |
| 3 | macOS app: SwiftUI chat UI skeleton talking to backend over WebSocket | 🚧 skeleton, unverified on real macOS |
| 4 | iPhone companion app | ⬜ deferred — macOS prioritized per current scope |
| 5 | Voice assistant: wake word, streaming STT/TTS, interrupt handling, offline mode | ⬜ |
| 6 | Memory: long-term store upgraded to vector embeddings (ChromaDB), project memory search | ⬜ (SQLite keyword store in place as the swappable placeholder) |
| 7 | GitHub integration: clone/create repos, commit, PR, code review, scaffolding, as plugins | ⬜ (plugin framework in place to host these) |
| 8 | Claude Code integration for "build software" workflows (plan → scaffold → generate → test → fix → commit loop) | ⬜ |
| 9 | Automation: email, calendar, reminders, file organization, meeting summaries, daily planning | ⬜ |
| 10 | Testing: expand unit/integration coverage, CI via GitHub Actions | 🚧 pytest suite started for backend; CI workflow not yet added |
| 11 | Optimization: performance, streaming latency, caching, telemetry (OpenTelemetry) | ⬜ |
| 12 | Production deployment: Docker Compose, Postgres/Redis, secrets management, monitoring | ⬜ (Dockerfile for backend added; full deployment stack not yet built) |

## What exists right now

- `backend/` — a real FastAPI service you can run locally:
  `/health`, `/api/chat`, `/ws/chat`, provider registry with Claude as
  default, SQLite-backed short/long-term/project memory stubs, a plugin
  loader with one example plugin (`system_info`). Covered by `pytest`.
- `apps/macos/JarvisMac/` — a SwiftUI Swift Package chat client skeleton.
  Not build-verified here (no macOS/Xcode toolchain in this environment).
- `ARCHITECTURE.md` — the design this is following.
- The pre-existing `jarviscli/` legacy CLI project is untouched.

## Explicitly deferred (not started)

iOS app, voice pipeline, vector memory, GitHub/Claude Code automation
plugins, macOS system-control plugins (Finder/Safari/Notes/etc.), Face
ID/Keychain security, the dashboard UI, and the full production deployment
stack (Postgres/Redis/Compose/CI). These are large enough that each
deserves its own focused session rather than a shallow stub claimed as
"done." This roadmap is the map for those follow-up sessions.
