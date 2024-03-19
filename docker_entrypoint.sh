#!/bin/sh
source .venv/bin/activate
cd /code/app

if [[ "$1" == "celery-worker" ]]; then
    celery -A celery_app.app worker  -l INFO
elif [[ "$1" == "celery-beat" ]]; then
    celery -A celery_app.app worker --beat -l INFO
else
    python manage.py create-db
    uvicorn main:app --host 0.0.0.0 --port 8000
fi
