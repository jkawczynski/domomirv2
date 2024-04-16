from collections.abc import Sequence
from datetime import date

from sqlalchemy import delete
from sqlmodel import col, select

from common.crud import Crud
from schedules.models import Schedule
from tasks.models import Task


class ScheduleCrud(Crud[Schedule]):
    model = Schedule

    def get_query(self):
        return super().get_query().order_by(col(Schedule.schedule_date))

    async def get_scheduled_for_day(
        self, day: date, exclude_ids: list[int] | None = None
    ) -> Sequence[Schedule]:
        exclude_ids = exclude_ids or []
        stmt = (
            select(Schedule)
            .where(Schedule.schedule_date == day)
            .where(Schedule.id not in exclude_ids)
        )
        result = await self.session.exec(stmt)
        return result.all()

    async def delete_all_finished(self):
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
        await self.session.exec(stmt)
        await self.session.commit()
