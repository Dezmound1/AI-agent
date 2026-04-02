#!/bin/sh
set -e
cd /app
echo "Applying Alembic migrations..."

uv run alembic upgrade head
echo "Seeding mock data (if empty)..."
uv run python scripts/seed_mock_data.py
echo "Starting application..."

exec uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
