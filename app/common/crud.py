from collections.abc import Sequence
from typing import Generic, TypeVar

from fastapi import Depends
from sqlmodel import SQLModel, delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from database import get_session

T = TypeVar("T", bound=SQLModel)


class Crud(Generic[T]):
    model: type[T]

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        self.session = session

    def get_query(self):
        return select(self.model)

    def get_details_query(self):
        return self.get_query()

    def filter_query(self, stmt, query: str | None):
        return stmt

    async def get_list(self, query: str | None = None) -> Sequence[T]:
        stmt = self.get_query()
        stmt = self.filter_query(stmt, query)
        result = await self.session.exec(stmt)
        return result.unique().all()

    async def get_by_id(self, instance_id: int) -> T | None:
        stmt = self.get_details_query().where(self.model.id == instance_id).distinct()
        result = await self.session.exec(stmt)
        return result.first()

    async def persist(self, instance: T):
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def delete(self, instance: T):
        stmt = delete(self.model).where(self.model.id == instance.id)
        await self.session.exec(stmt)
        await self.session.commit()

    async def persist_all(self, instances: list[T]):
        for item in instances:
            self.session.add(item)

        await self.session.commit()
