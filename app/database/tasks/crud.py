from collections.abc import Iterable, Sequence

from database.tasks.models import Task
from sqlalchemy import delete, func
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession


async def get_list(session: AsyncSession) -> Sequence[Task]:
    stmt = select(Task).order_by(col(Task.completed).desc(), col(Task.id))
    result = await session.exec(stmt)
    return result.all()


async def get_unfinished(session: AsyncSession) -> Sequence[Task]:
    stmt = select(Task).where(col(Task.completed).is_(None))
    result = await session.exec(stmt)
    return result.all()


async def get_unfinished_count(session: AsyncSession) -> int:
    stmt = select(func.count(col(Task.id))).where(col(Task.completed).is_(None))
    result = await session.scalar(stmt)
    return result or 0


async def get_by_id(session: AsyncSession, task_id: int) -> Task | None:
    stmt = select(Task).where(Task.id == task_id)
    result = await session.exec(stmt)
    return result.first()


async def persist(session: AsyncSession, task: Task) -> Task:
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def persist_all(session: AsyncSession, tasks: Iterable[Task]):
    for task in tasks:
        session.add(task)

    await session.commit()


async def remove_all_finished(session: AsyncSession):
    stmt = delete(Task).where(col(Task.completed).is_not(None))
    await session.exec(stmt)
    await session.commit()
