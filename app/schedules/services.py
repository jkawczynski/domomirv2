from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from schedules import crud, models


async def create_schedule(
    session: AsyncSession, schedule: models.ScheduleCreate
) -> models.Schedule:
    db_schedule = models.Schedule.model_validate(schedule)
    return await crud.persist(session, db_schedule)


async def edit_schedule(
    session: AsyncSession,
    input_schedule: models.ScheduleCreate,
    schedule_id: int,
) -> models.Schedule:
    schedule = await crud.get_by_id(session, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    schedule.name = input_schedule.name
    schedule.schedule_date = input_schedule.schedule_date
    schedule.frequency_in_days = input_schedule.frequency_in_days
    schedule = await crud.persist(session, schedule)
    return schedule
