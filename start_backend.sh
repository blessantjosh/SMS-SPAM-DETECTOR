#!/bin/bash
echo "====================================="
echo "CyberSentinel AI - Starting Backend"
echo "====================================="
cd "$(dirname "$0")/backend"
source ../venv/Scripts/activate
echo "Backend API will run on http://localhost:8000"
echo "API docs: http://localhost:8000/docs"
echo "Press Ctrl+C to stop"
echo "====================================="
python main.py
