#!/usr/bin/env bash

set -e

alembic upgrade head

gunicorn main:app --bind 0.0.0.0:8001 --workers 4 --worker-class uvicorn.workers.UvicornH11Worker --log-file=- --access-logfile=- --error-logfile=-