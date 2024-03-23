from datetime import datetime

from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from integrations.mqtt.tasks import send_mqtt_task_assigned
from schedules.tasks import update_schedule
from tasks import crud, models
from users import crud as users_crud


async def create_task(session: AsyncSession, task: models.TaskCreate) -> None:
    db_task = models.Task.model_validate(task)
    await crud.persist(session, db_task)


async def update_task(
    session: AsyncSession,
    task_id: int,
    task: models.TaskEdit,
) -> None:
    db_task = await crud.get_by_id(session, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task.model_dump(exclude_defaults=True)
    await _partial_update(session, db_task, update_data)

    # send background tasks
    if update_data.get("completed") and db_task.schedule_id:
        await update_schedule.kiq(db_task.schedule_id)

    if update_data.get("assigned_to_id") and db_task.assigned_to_id:
        await send_mqtt_task_assigned.kiq(db_task.id)


async def _partial_update(
    session: AsyncSession, db_task: models.Task, update_data: dict
):
    if "completed" in update_data:
        db_task.completed = datetime.now() if update_data["completed"] else None

    if "assigned_to_id" in update_data:
        user = await users_crud.get_by_id(session, update_data["assigned_to_id"])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        db_task.assigned_to = user

    await crud.persist(session, db_task)
