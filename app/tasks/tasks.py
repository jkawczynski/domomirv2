import logging
from datetime import date

from celery import shared_task
from database import engine
from database.schedules import crud as schedules_crud
from database.tasks import crud, models
from sqlmodel import Session

logger = logging.getLogger(__name__)


@shared_task
def create_tasks_for_today():
    with Session(engine) as db:
        unfinished_tasks = crud.get_unfinished(db)
        today = date.today()

        scheduled_tasks = schedules_crud.get_scheduled_for_day(
            db=db,
            day=today,
            exclude_ids=[
                task.schedule_id for task in unfinished_tasks if task.schedule_id
            ],
        )

        tasks = [
            models.Task(
                name=scheduled_task.name,
                task_date=today,
                schedule_id=scheduled_task.id,
            )
            for scheduled_task in scheduled_tasks
        ]

        crud.persist_all(db, tasks)


@shared_task
def clean_finished_tasks_and_schedules():
    with Session(engine) as db:
        crud.remove_all_finished(db)
        schedules_crud.remove_all_finished(db)
