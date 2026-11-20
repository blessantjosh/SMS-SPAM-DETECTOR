#!/bin/bash
echo "======================================"
echo "CyberSentinel AI - Starting Frontend"
echo "======================================"
cd "$(dirname "$0")/cybersentinel-dashboard"
echo "Frontend will run on http://localhost:4200"
echo "Press Ctrl+C to stop"
echo "======================================"
npm start
