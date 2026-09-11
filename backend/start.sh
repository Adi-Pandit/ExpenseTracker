#!/bin/sh
# Entrypoint for the ECS container.
# Runs migrations then starts gunicorn.
set -e

echo "[start.sh] Running database migrations..."
python manage.py migrate --no-input

echo "[start.sh] Starting gunicorn on 0.0.0.0:8000..."
exec gunicorn ExpenseTracker.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --threads 4 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
