from celery_app import create_celery
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


def create_app():
    app = FastAPI()

    app.celery_app = create_celery()

    from routers import cat, schedules, tasks, users

    app.include_router(tasks.router, tags=["tasks"])
    app.include_router(schedules.router, prefix="/schedules", tags=["schedules"])
    app.include_router(users.router, prefix="/users", tags=["users"])
    app.include_router(cat.router, prefix="/cat", tags=["cat"])

    app.mount("/static", StaticFiles(directory="static"), name="static")

    return app


app = create_app()
celery = app.celery_app
