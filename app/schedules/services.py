from fastapi import Depends, HTTPException

from schedules import models
from schedules.crud import ScheduleCrud


class ScheduleService:
    def __init__(self, crud: ScheduleCrud = Depends(ScheduleCrud)) -> None:
        self.crud = crud

    async def create_schedule(self, schedule: models.ScheduleCreate) -> models.Schedule:
        db_schedule = models.Schedule.model_validate(schedule)
        return await self.crud.persist(db_schedule)

    async def edit_schedule(
        self,
        input_schedule: models.ScheduleCreate,
        schedule_id: int,
    ) -> models.Schedule:
        schedule = await self.crud.get_by_id(schedule_id)
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")

        schedule.name = input_schedule.name
        schedule.schedule_date = input_schedule.schedule_date
        schedule.frequency_in_days = input_schedule.frequency_in_days
        schedule = await self.crud.persist(schedule)
        return schedule
