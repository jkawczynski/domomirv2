from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class RecipeIngredientBase(SQLModel):
    name: str = Field(min_length=2, max_length=255)
    amount_and_unit: str | None = Field(default=None, nullable=True)


class RecipeIngredient(RecipeIngredientBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    recipe_id: int | None = Field(default=None, foreign_key="recipe.id", nullable=True)
    recipe: Optional["Recipe"] = Relationship(back_populates="ingredients")


class RecipeIngredientCreate(RecipeIngredientBase):
    pass


class RecipeImageBase(SQLModel):
    file_name: str


class RecipeImage(RecipeImageBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    recipe_id: int | None = Field(default=None, foreign_key="recipe.id", nullable=True)
    recipe: Optional["Recipe"] = Relationship(back_populates="images")


class RecipeBase(SQLModel):
    name: str = Field(min_length=3, max_length=255)
    url: str | None = Field(default=None, nullable=True)
    description: str | None = Field(default=None, nullable=True)


class Recipe(RecipeBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    images: list["RecipeImage"] = Relationship(back_populates="recipe")
    ingredients: list["RecipeIngredient"] = Relationship(back_populates="recipe")


class RecipeCreate(RecipeBase):
    ingredients: list[RecipeIngredient]


class RecipeIngredientsIds(SQLModel):
    ingredients: list[int]
