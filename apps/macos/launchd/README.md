# JARVIS backend as a background service (macOS LaunchAgent)

Runs the backend automatically at login instead of needing `poetry run
python -m jarvis_backend.main` in a terminal every time. Managed by
`launchd`, the same mechanism macOS uses for its own background services.

**Not build/run-verified** — written without access to a Mac in this
session. Review `com.jarvis.backend.plist.template` before installing if
you want to know exactly what it does; it's a short, plain plist.

## Install

Requires the backend already set up once (`backend/.env` with your
Anthropic API key — see `backend/README.md`).

```bash
cd apps/macos/launchd
./install.sh
```

This starts the backend immediately and arranges for it to start again
automatically every time you log in. It restarts itself if it ever exits
(crash or otherwise) while installed.

## Where things go

- **Logs** (stdout/stderr, including the token printed on first run):
  `~/Library/Logs/jarvis-backend.log` and `jarvis-backend-error.log`
- **Service definition**: `~/Library/LaunchAgents/com.jarvis.backend.plist`
  (a filled-in copy of the template — regenerated each time you run
  `install.sh`, so don't hand-edit it; edit the template and reinstall)

## Check on it

```bash
launchctl print gui/$(id -u)/com.jarvis.backend
tail -f ~/Library/Logs/jarvis-backend.log
```

## Remove it

```bash
cd apps/macos/launchd
./uninstall.sh
```

Stops the backend and removes the LaunchAgent — nothing starts
automatically after this. The macOS app (the chat window) is unaffected
either way; it's still launched manually with `swift run` per
`apps/macos/JarvisMac/README.md`.
