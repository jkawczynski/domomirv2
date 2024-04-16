from collections.abc import Sequence

from sqlalchemy import delete, func
from sqlalchemy.orm import joinedload
from sqlmodel import col, select

from common.crud import Crud
from tasks.models import Task


class TaskCrud(Crud[Task]):
    model = Task

    def get_query(self):
        return super().get_query().order_by(col(Task.completed).desc(), col(Task.id))

    def get_details_query(self):
        return super().get_details_query().options(joinedload(Task.assigned_to))

    async def get_unfinished(self) -> Sequence[Task]:
        stmt = select(Task).where(col(Task.completed).is_(None))
        result = await self.session.exec(stmt)
        return result.all()

    async def get_unfinished_count(self) -> int:
        stmt = select(func.count(col(Task.id))).where(col(Task.completed).is_(None))
        result = await self.session.scalar(stmt)
        return result or 0

    async def delete_all_finished(self):
        stmt = delete(Task).where(col(Task.completed).is_not(None))
        await self.session.exec(stmt)
        await self.session.commit()
