import logging
from datetime import date, timedelta

from database import get_session
from schedules import crud
from tkq import broker

logger = logging.getLogger(__name__)


@broker.task()
async def update_schedule(schedule_id: int) -> None:
    session_maker = get_session()
    session = await anext(session_maker)

    schedule = await crud.get_by_id(session, schedule_id)
    if not schedule:
        return

    frequency_in_days = schedule.frequency_in_days
    if not frequency_in_days:
        await crud.remove(session, schedule)
        return

    target_date = schedule.schedule_date
    while target_date <= date.today():
        target_date = target_date + timedelta(days=frequency_in_days)

    schedule.schedule_date = target_date
    await crud.persist(session, schedule)
