#!/bin/bash

# Resolve project root relative to this script
# this script is at run_backend.sh (Project Root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

cd "$PROJECT_ROOT"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Installing dependencies..."
    venv/bin/pip install -r backend/requirements.txt
fi

echo "Starting Backend Server from $PROJECT_ROOT..."
venv/bin/uvicorn backend.main:app --reload
