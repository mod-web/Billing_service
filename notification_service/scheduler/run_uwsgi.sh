#!/usr/bin/env bash

set -e

python manage.py migrate

python manage.py collectstatic --no-input

#python manage.py createsuperuser --noinput || true

uwsgi --strict --ini /app/uwsgi/uwsgi.ini