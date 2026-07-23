#!/bin/bash
# Stops the JARVIS backend LaunchAgent and removes it — the backend will no
# longer start automatically at login. Run this on your Mac.
set -euo pipefail

LABEL="com.jarvis.backend"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"

launchctl bootout "gui/$(id -u)" "$PLIST" 2>/dev/null || true
rm -f "$PLIST"

echo "Removed $LABEL — the backend will no longer start automatically."
