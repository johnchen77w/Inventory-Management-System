#!/bin/bash
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting API server..."
if [ "$ENVIRONMENT" = "development" ]; then
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
else
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
fi
