#!/bin/bash
# Hound Kiosk Mode Launcher
# This script launches Hound in full-screen kiosk mode using Firefox

# Configuration
HOUND_URL="http://localhost:3000"

# Try to find Firefox
if command -v firefox-esr >/dev/null 2>&1; then
    BROWSER="firefox-esr"
elif command -v firefox >/dev/null 2>&1; then
    BROWSER="firefox"
else
    echo "Firefox not found. Please install firefox-esr or firefox."
    exit 1
fi

# Kill any existing Firefox instances
pkill -f "$BROWSER" || true

# Wait a moment for processes to terminate
sleep 2

# Launch Firefox in kiosk mode
# --kiosk: Full screen, no chrome
# --new-instance: New browser instance
# --private-window: Private browsing (optional)
# --width 1920 --height 1080: Set resolution
exec "$BROWSER" \
    --kiosk \
    --new-instance \
    "$HOUND_URL"
