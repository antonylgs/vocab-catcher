#!/usr/bin/env bash
# Install/uninstall vocab-catcher as a macOS launchd user agent.
# Paths are resolved dynamically, so it works wherever the project lives.
set -euo pipefail

LABEL="com.ags.vocab-catcher"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$DIR/$LABEL.plist.template"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"

uninstall() {
    launchctl unload "$PLIST" 2>/dev/null || true
    rm -f "$PLIST"
    echo "Uninstalled $LABEL"
}

if [[ "${1:-}" == "uninstall" ]]; then
    uninstall
    exit 0
fi

# Prefer the project's venv python, fall back to `uv run` resolution.
if [[ -x "$DIR/.venv/bin/python3" ]]; then
    PYTHON="$DIR/.venv/bin/python3"
else
    echo "No .venv found at $DIR/.venv — run 'uv sync' first." >&2
    exit 1
fi

mkdir -p "$HOME/Library/LaunchAgents"
sed -e "s#__PYTHON__#$PYTHON#g" -e "s#__DIR__#$DIR#g" "$TEMPLATE" > "$PLIST"

launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"
echo "Installed and loaded $LABEL"
echo "Logs: $DIR/bot.log"
