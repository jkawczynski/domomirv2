from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from tasks.models import Task


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)

    tasks: list["Task"] = Relationship(back_populates="assigned_to")


class UserCreate(SQLModel):
    name: str
