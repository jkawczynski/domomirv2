from sqlmodel import Field, SQLModel


class RecipeBase(SQLModel):
    name: str = Field(min_length=3, max_length=255)
    url: str | None = Field(default=None, nullable=True)
    description: str | None = Field(default=None, nullable=True)


class Recipe(RecipeBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
