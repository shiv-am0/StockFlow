#!/bin/sh
set -e

host="0.0.0.0"
port="${PORT:-8000}"

echo "Running database migrations..."
alembic upgrade head

echo "Starting StockFlow API on $host:$port..."
exec uvicorn app.main:app --host "$host" --port "$port"
