from datetime import date, datetime, timedelta

from database.schedules import crud as schedule_crud
from database.tasks import crud, models
from database.users import crud as users_crud
from fastapi import HTTPException
from integrations.mqtt.tasks import send_mqtt_task_assigned
from sqlmodel.ext.asyncio.session import AsyncSession


async def create_task(session: AsyncSession, task: models.TaskCreate) -> None:
    db_task = models.Task.model_validate(task)
    await crud.persist(session, db_task)


async def assign_task(session: AsyncSession, task_id: int, user_id: int) -> None:
    task = await crud.get_by_id(session, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    user = await users_crud.get_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    task.assigned_to = user
    await crud.persist(session, task)
    await send_mqtt_task_assigned.kiq(task.id)


async def undo_complete_task(session: AsyncSession, task_id: int) -> None:
    task = await crud.get_by_id(session, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.completed = None
    await crud.persist(session, task)


async def complete_task(session: AsyncSession, task_id: int) -> None:
    task = await crud.get_by_id(session, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.completed:
        return

    task.completed = datetime.now()
    await crud.persist(session, task)

    if task.schedule_id and (
        schedule := await schedule_crud.get_by_id(session, task.schedule_id)
    ):
        frequency_in_days = schedule.frequency_in_days
        if not frequency_in_days:
            await schedule_crud.remove(session, schedule)
            return

        target_date = schedule.schedule_date
        while target_date <= date.today():
            target_date = target_date + timedelta(days=frequency_in_days)

        schedule.schedule_date = target_date
        await schedule_crud.persist(session, schedule)
