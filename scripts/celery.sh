celery -A core.celery worker -E --loglevel=info --hostname=worker.basic --concurrency=3
