from collections.abc import Sequence

from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from . import models


async def get_list(session: AsyncSession) -> Sequence[models.User]:
    stmt = select(models.User).order_by(col(models.User.id).desc())
    result = await session.exec(stmt)
    return result.all()


async def get_by_id(session: AsyncSession, user_id: int) -> models.User | None:
    stmt = select(models.User).where(models.User.id == user_id)
    result = await session.exec(stmt)
    return result.first()


async def get_by_name(session: AsyncSession, name: str) -> models.User | None:
    stmt = select(models.User).where(models.User.name == name)
    result = await session.exec(stmt)
    return result.first()


async def persist(session: AsyncSession, user: models.User) -> models.User:
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
