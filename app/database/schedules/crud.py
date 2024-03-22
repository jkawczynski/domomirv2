from collections.abc import Sequence
from datetime import date

from database.schedules.models import Schedule
from database.tasks.models import Task
from sqlalchemy import delete
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession


async def get_list(session: AsyncSession) -> Sequence[Schedule]:
    stmt = select(Schedule).order_by(col(Schedule.schedule_date))
    result = await session.exec(stmt)
    return result.all()


async def get_scheduled_for_day(
    session: AsyncSession, day: date, exclude_ids: list[int] | None = None
) -> Sequence[Schedule]:
    exclude_ids = exclude_ids or []
    stmt = (
        select(Schedule)
        .where(Schedule.schedule_date == day)
        .where(Schedule.id not in exclude_ids)
    )
    result = await session.exec(stmt)
    return result.all()


async def get_by_id(session: AsyncSession, schedule_id: int) -> Schedule | None:
    stmt = select(Schedule).where(Schedule.id == schedule_id)
    result = await session.exec(stmt)
    return result.first()


async def persist(session: AsyncSession, schedule: Schedule) -> Schedule:
    session.add(schedule)
    await session.commit()
    await session.refresh(schedule)
    return schedule


async def remove(session: AsyncSession, schedule: Schedule):
    await session.delete(schedule)
    await session.commit()


async def remove_all_finished(session: AsyncSession):
    today = date.today()
    subquery = (
        select(Task.schedule_id)
        .where(col(Task.completed).is_(None))
        .where(col(Task.schedule_id).is_not(None))
        .scalar_subquery()
    )

    stmt = (
        delete(Schedule)
        .where(col(Schedule.schedule_date) < today)
        .where(col(Schedule.id).not_in(subquery))
    )
    await session.exec(stmt)
    await session.commit()
