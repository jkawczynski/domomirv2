from datetime import date, datetime
from typing import TYPE_CHECKING, ClassVar, Optional

from sqlalchemy.ext.hybrid import hybrid_property
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.database.schedules.models import Schedule
    from app.database.users.models import User


# Workaround until sqlmodel supports hybrid properties
def _is_overdue(self) -> bool:
    return self.task_date < date.today()


class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    completed: datetime | None = None
    task_date: date
    schedule_id: int | None = Field(
        default=None,
        foreign_key="schedule.id",
        nullable=True,
    )
    assigned_to_id: int | None = Field(
        default=None,
        foreign_key="user.id",
        nullable=True,
    )

    schedule: Optional["Schedule"] = Relationship(back_populates="tasks")
    assigned_to: Optional["User"] = Relationship(back_populates="tasks")

    is_overdue: ClassVar[bool] = hybrid_property(_is_overdue)


class TaskCreate(SQLModel):
    name: str
    task_date: date = Field(default_factory=lambda: date.today())


class TaskEdit(SQLModel):
    completed: bool | None = Field(default=None)
    assigned_to_id: int | None = Field(default=None)
