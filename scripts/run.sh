#!/bin/sh
python3 manage.py migrate
celery -A core.celery worker -E --loglevel=info --hostname=worker.basic --concurrency=3 &
python3 manage.py runserver 0.0.0.0:8000