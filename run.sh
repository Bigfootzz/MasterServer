#!/bin/sh
# Revelade Revolution MasterServer - Linux/macOS launcher
# Creates a virtualenv on first run, installs dependencies, starts the server.
set -e
cd "$(dirname "$0")"
if [ ! -d .venv ]; then
    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt
fi
exec .venv/bin/python run.py
