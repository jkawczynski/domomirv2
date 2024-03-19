#!/bin/sh
source .venv/bin/activate
cd /code/app

if [[ "$1" == "celery-worker" ]]; then
    celery -A main.celery worker  -l INFO
elif [[ "$1" == "celery-beat" ]]; then
    celery -A main.celery beat -l INFO
else
    python manage.py create-db
    uvicorn main:app --host 0.0.0.0 --port 8000
fi
