from datetime import date
from typing import TYPE_CHECKING

import humanize
from pydantic import field_validator
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from tasks.models import Task


class ScheduleBase(SQLModel):
    name: str = Field(min_length=3, max_length=255)
    schedule_date: date
    frequency_in_days: int | None = Field(default=None, gt=0, lt=366)

    @property
    def day(self) -> str:
        return humanize.naturalday(self.schedule_date, format="%A, %b %d")


class Schedule(ScheduleBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    tasks: list["Task"] = Relationship(back_populates="schedule")


class ScheduleCreate(ScheduleBase):
    @field_validator("schedule_date")
    @classmethod
    def check_if_schedule_date_is_future(cls, val: date) -> date:
        assert val > date.today(), "this must be a future date"
        return val
