from collections.abc import Sequence

from sqlalchemy.orm import joinedload
from sqlmodel import col, select, update
from sqlmodel.ext.asyncio.session import AsyncSession

from recipes.models import Recipe, RecipeImage, RecipeIngredient


async def get_list(session: AsyncSession, query: str | None = None) -> Sequence[Recipe]:
    stmt = (
        select(Recipe)
        .order_by(col(Recipe.id).desc())
        .options(joinedload(Recipe.images))
    )
    if query:
        stmt = stmt.where(col(Recipe.name).icontains(query))

    result = await session.exec(stmt)
    return result.unique()


async def get_ingredients_by_ids(
    session: AsyncSession, ingredients_ids: list[int]
) -> Sequence[RecipeIngredient]:
    stmt = select(RecipeIngredient).where(col(RecipeIngredient.id).in_(ingredients_ids))
    result = await session.exec(stmt)
    return result.all()


async def get_by_id(session: AsyncSession, recipe_id: int) -> Recipe | None:
    stmt = (
        select(Recipe)
        .order_by(col(Recipe.id).desc())
        .options(joinedload(Recipe.images))
        .options(joinedload(Recipe.ingredients))
        .where(Recipe.id == recipe_id)
        .distinct()
    )
    result = await session.exec(stmt)
    return result.first()


async def persist(session: AsyncSession, recipe_image: RecipeImage | Recipe):
    session.add(recipe_image)
    await session.commit()
    await session.refresh(recipe_image)
    return recipe_image


async def connect_recipe_with_images(
    session: AsyncSession,
    recipe: Recipe,
    images_ids: list[int],
):
    stmt = (
        update(RecipeImage)
        .where(RecipeImage.id.in_(images_ids))
        .values(recipe_id=recipe.id)
    )
    await session.exec(stmt)
    await session.commit()


async def get_images_by_ids(
    session: AsyncSession,
    images_ids: list[int],
) -> list[RecipeImage]:
    stmt = select(RecipeImage).where(col(RecipeImage.id).in_(images_ids))
    result = await session.exec(stmt)
    return list(result.all())
