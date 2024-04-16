import asyncio
from datetime import date

from database import get_session
from integrations.wastes import schedule
from tasks import models
from tasks.crud import TaskCrud
from tasks.services import TaskService
from tkq import DEFAULT_SCHEDULE_ARGS, broker


async def _check_schedule_and_create_task(
    service: TaskService, schedule: dict, task_name: str
):
    today = date.today()
    year, month, day = today.year, today.month, today.day
    pickup_dates = schedule.get(year, {}).get(month)

    # subtract one day to create task day before pickup
    if pickup_dates and day in [d - 1 for d in pickup_dates]:
        await service.create_task(models.TaskCreate(name=task_name))


@broker.task(schedule=[{"cron": "0 2 * * *", **DEFAULT_SCHEDULE_ARGS}])
async def create_task_to_prepare_wastes():
    session_maker = get_session()
    session = await anext(session_maker)
    service = TaskService(TaskCrud(session))

    mixed_wastes = _check_schedule_and_create_task(
        service,
        schedule=schedule.SCHEDULE_MIXED_WASTES,
        task_name="Wystawić kubeł na śmieci mieszane",
    )
    segregated_wastes = _check_schedule_and_create_task(
        service,
        schedule=schedule.SCHEDULE_SEGREGATED_WASTES,
        task_name="Wystawić śmieci segregowane",
    )
    await asyncio.gather(mixed_wastes, segregated_wastes)
