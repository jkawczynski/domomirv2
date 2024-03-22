#!/bin/sh
source .venv/bin/activate
cd /code/app

if [[ "$1" == "worker" ]]; then
    taskiq worker tkq:broker -fsd
elif [[ "$1" == "scheduler" ]]; then
    taskiq scheduler tkq:scheduler -fsd
else
    alembic upgrade head
    uvicorn main:app --host 0.0.0.0 --port 8000
fi
