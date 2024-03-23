import asyncio
import logging
from datetime import date

from database import get_session, session_maker
from schedules import crud as schedules_crud
from tasks import crud, models
from tkq import DEFAULT_SCHEDULE_ARGS, broker

logger = logging.getLogger(__name__)


@broker.task(schedule=[{"cron": "0 2 * * *", **DEFAULT_SCHEDULE_ARGS}])
async def create_tasks_for_today():
    session_maker = get_session()
    session = await anext(session_maker)

    unfinished_tasks = await crud.get_unfinished(session)
    today = date.today()

    scheduled_tasks = await schedules_crud.get_scheduled_for_day(
        session=session,
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

    await crud.persist_all(session, tasks)


@broker.task(schedule=[{"cron": "0 2 * * *", **DEFAULT_SCHEDULE_ARGS}])
async def clean_finished_tasks_and_schedules():
    remove_tasks = crud.remove_all_finished(session_maker())
    remove_schedules = schedules_crud.remove_all_finished(session_maker())
    asyncio.gather(remove_tasks, remove_schedules)
