from datetime import date

from celery import shared_task
from database import engine
from database.tasks import models
from integrations.wastes import schedule
from services import tasks as tasks_service
from sqlmodel import Session


def _check_schedule_and_create_task(db: Session, schedule: dict, task_name: str):
    today = date.today()
    year, month, day = today.year, today.month, today.day
    pickup_dates = schedule.get(year, {}).get(month)

    # subtract one day to create task day before pickup
    if pickup_dates and day in [d - 1 for d in pickup_dates]:
        tasks_service.create_task(db, models.TaskCreate(name=task_name))


@shared_task
def create_task_to_prepare_wastes():
    with Session(engine) as db:
        _check_schedule_and_create_task(
            db,
            schedule=schedule.SCHEDULE_MIXED_WASTES,
            task_name="Wystawić kubeł na śmieci mieszane",
        )
        _check_schedule_and_create_task(
            db,
            schedule=schedule.SCHEDULE_SEGREGATED_WASTES,
            task_name="Wystawić śmieci segregowane",
        )
