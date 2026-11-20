#!/usr/bin/env bash
# Chhand Local Development Startup Script

set -e

# Change to repository root
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DIR"

echo "=================================================="
echo " Starting Chhand Literary Studio..."
echo " Backend: FastAPI"
echo " Frontend: http://127.0.0.1:8000"
echo " API Docs: http://127.0.0.1:8000/docs"
echo "=================================================="

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
