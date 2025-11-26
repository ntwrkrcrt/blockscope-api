#!/bin/sh
set -e

echo "Starting app..."

exec gunicorn --workers 2 --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8021 \
    --worker-connections 1000 main:app