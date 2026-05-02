#!/usr/bin/env sh
set -e
PORT="${PORT:-8000}"
python -m alembic upgrade head
exec python -m uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
