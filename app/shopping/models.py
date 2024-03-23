from datetime import datetime

from sqlmodel import Field, SQLModel


class ShoppingListItemBase(SQLModel):
    name: str = Field(min_length=3, max_length=255)
    completed: datetime | None = Field(default=None, nullable=True)


class ShoppingListItem(ShoppingListItemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class ShoppingListItemCreate(ShoppingListItemBase):
    pass


class ShoppingListItemEdit(ShoppingListItemBase):
    name: str | None = Field(default=None, min_length=3, max_length=255)
