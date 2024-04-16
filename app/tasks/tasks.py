import logging
from datetime import date

from database import get_session
from schedules.crud import ScheduleCrud
from tasks import models
from tasks.crud import TaskCrud
from tkq import DEFAULT_SCHEDULE_ARGS, broker

logger = logging.getLogger(__name__)


@broker.task(schedule=[{"cron": "0 2 * * *", **DEFAULT_SCHEDULE_ARGS}])
async def create_tasks_for_today():
    session_maker = get_session()
    session = await anext(session_maker)
    task_crud = TaskCrud(session)
    schedule_crud = ScheduleCrud(session)

    unfinished_tasks = await task_crud.get_unfinished()
    today = date.today()

    scheduled_tasks = await schedule_crud.get_scheduled_for_day(
        day=today,
        exclude_ids=[task.schedule_id for task in unfinished_tasks if task.schedule_id],
    )

    tasks = [
        models.Task(
            name=scheduled_task.name,
            task_date=today,
            schedule_id=scheduled_task.id,
        )
        for scheduled_task in scheduled_tasks
    ]

    await task_crud.persist_all(tasks)


@broker.task(schedule=[{"cron": "0 2 * * *", **DEFAULT_SCHEDULE_ARGS}])
async def clean_finished_tasks_and_schedules():
    session_maker = get_session()
    session = await anext(session_maker)
    task_crud = TaskCrud(session)
    schedule_crud = ScheduleCrud(session)
    await task_crud.delete_all_finished()
    await schedule_crud.delete_all_finished()
