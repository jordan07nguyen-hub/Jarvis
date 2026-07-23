#!/bin/bash
# Installs the JARVIS backend as a macOS LaunchAgent: starts automatically
# at login, restarts itself if it ever exits. Run this on your Mac (not in
# this repo's CI/dev environment) — it writes into your own ~/Library.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
BACKEND_DIR="$REPO_ROOT/backend"
LABEL="com.jarvis.backend"
PLIST_DEST="$HOME/Library/LaunchAgents/$LABEL.plist"

POETRY_PATH="$(command -v poetry || echo "$HOME/.local/bin/poetry")"
if [ ! -x "$POETRY_PATH" ]; then
    echo "error: poetry not found at $POETRY_PATH" >&2
    echo "  install it first: curl -sSL https://install.python-poetry.org | python3 -" >&2
    exit 1
fi

if [ ! -f "$BACKEND_DIR/.env" ]; then
    echo "warning: $BACKEND_DIR/.env not found." >&2
    echo "  cp backend/.env.example backend/.env and set JARVIS_ANTHROPIC_API_KEY before the service is useful." >&2
fi

mkdir -p "$HOME/Library/LaunchAgents" "$HOME/Library/Logs"

sed \
    -e "s|__POETRY_PATH__|$POETRY_PATH|g" \
    -e "s|__BACKEND_DIR__|$BACKEND_DIR|g" \
    -e "s|__HOME__|$HOME|g" \
    "$SCRIPT_DIR/com.jarvis.backend.plist.template" > "$PLIST_DEST"

# Reload cleanly if this was already installed (e.g. re-running after an update).
launchctl bootout "gui/$(id -u)" "$PLIST_DEST" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST_DEST"

echo "Installed and started: $LABEL"
echo "Logs:   $HOME/Library/Logs/jarvis-backend.log"
echo "        $HOME/Library/Logs/jarvis-backend-error.log"
echo "Status: launchctl print gui/$(id -u)/$LABEL"
echo "Remove: apps/macos/launchd/uninstall.sh"
