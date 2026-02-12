#!/bin/bash

# Italian Learning Companion - Web App Launcher
# Run this script to start the Flask server

echo "🇮🇹 Starting Italian Learning Companion Web App..."
echo ""
echo "The app will be available at:"
echo "  - http://localhost:5001 (this computer)"
echo "  - http://$(ipconfig getifaddr en0 2>/dev/null || hostname):5001 (mobile devices on same network)"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd "$(dirname "$0")"
python3 app.py
