# JARVIS — Architecture (macOS-first)

This document describes the new JARVIS AI assistant architecture, distinct
from the legacy command-line assistant that lives in [`jarviscli/`](jarviscli/)
(kept as-is, unaffected by this work).

Scope note: this is being built incrementally. See [ROADMAP.md](ROADMAP.md)
for what's implemented today versus planned. Nothing here is claimed to be
"production-ready" until it has working, tested code behind it.

## Goals

- Feel like a real assistant, not a chatbot: persistent memory, tool use,
  and control over the local machine.
- macOS-first. iOS and other platforms are deferred until the macOS
  experience and backend are solid.
- Provider-agnostic reasoning: Claude is the default and primary provider,
  with OpenAI, local Ollama, Gemini, and OpenRouter as swappable
  alternatives via config, not code changes.
- Small, composable modules — a plugin can be added without touching core
  code, a new provider can be added by implementing one interface.

## High-level components

```
                     ┌─────────────────────────┐
                     │   apps/macos/JarvisMac   │  SwiftUI menu-bar/window app
                     │   (Swift Package)        │  chat UI, WebSocket client
                     └───────────┬──────────────┘
                                 │ WebSocket (/ws/chat) + REST (/api/*)
                     ┌───────────▼──────────────┐
                     │   backend/ (FastAPI)      │
                     │                           │
                     │  api/        routes, ws   │
                     │  providers/  AI backends   │
                     │  memory/     short/long/   │
                     │              project store │
                     │  plugins/    tool calling   │
                     │  core/       config, app    │
                     └───────────┬───────────────┘
                                 │
              ┌──────────────────┼───────────────────┐
              ▼                  ▼                    ▼
        Claude API         Local Ollama          OpenAI / Gemini /
        (default)          (offline mode)        OpenRouter
```

## Backend (`backend/`)

FastAPI application, managed with Poetry.

- `core/config.py` — Pydantic settings. Single source of truth for which
  AI provider is active, API keys (read from environment / `.env`, never
  committed), server host/port, memory paths.
- `providers/` — one module per AI backend, all implementing the same
  `AIProvider` interface (`is_configured()`, `chat()`, `stream_chat()`).
  A `registry.py` resolves the active provider using the configured
  priority order: **Claude → OpenAI → Ollama → Gemini → OpenRouter**,
  picking the first one that's actually configured unless the user pins
  one explicitly.
- `memory/` — three stores behind a common interface:
  - `ShortTermMemory`: in-process, per-session rolling conversation buffer.
  - `LongTermMemory`: SQLite-backed durable facts/preferences, keyword
    search today; the interface is written so a vector store (ChromaDB)
    can be swapped in later (Phase 6) without changing callers.
  - `ProjectMemory`: per-project notes/context, also SQLite-backed.
- `plugins/` — a minimal tool-calling framework. Each plugin subclasses
  `Plugin`, declares a name/description/args, and implements `run()`. The
  `PluginLoader` discovers plugins under `plugins/installed/` at startup.
  This is the extension point for macOS system control (Finder, Safari,
  Notes, etc.) and GitHub actions in later phases — each becomes a plugin,
  not a special case in the core.
- `api/` — REST endpoints (`/health`, `/api/chat`) and a WebSocket endpoint
  (`/ws/chat`) for streaming conversation, which the macOS app uses.

## macOS app (`apps/macos/JarvisMac/`)

A Swift Package (macOS 14+) with an executable SwiftUI target — no Xcode
project file required to get started; `swift run` launches it as a native
window app. It talks to the backend over the WebSocket chat endpoint.
This is a UI skeleton today (message list, input field, connection status)
— the deeper macOS system integrations (Shortcuts, App Intents, Keychain,
Face ID, menu-bar orb, voice) are Phase 3+ work tracked in the roadmap.

Building/running this app requires a real Mac with Xcode command line
tools; it has not been build-verified in this (Linux) session — treat it
as a reviewed-but-unverified skeleton until someone runs it on macOS.

## Configuration

All secrets and environment-specific values live in `backend/.env`
(git-ignored), following `backend/.env.example`. Nothing is hard-coded.

## Why this shape

- Provider swapping and plugin/tool addition are the two things the spec
  asks for repeatedly (multiple AI backends, macOS control, GitHub
  actions, automations) — so those are the two seams the architecture is
  built around, rather than being bolted on later.
- Memory is split into three concerns because they have different
  lifetimes and query patterns (a conversation buffer is not a durable
  fact store), even though today's long-term store is a simple SQLite
  table rather than a vector DB — swapping the storage engine later
  shouldn't require touching call sites.
