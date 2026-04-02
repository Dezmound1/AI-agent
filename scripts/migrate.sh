#!/bin/sh
set -e
cd "$(dirname "$0")/.."
exec uv run alembic upgrade head
