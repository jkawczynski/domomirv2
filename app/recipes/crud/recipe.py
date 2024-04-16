from sqlalchemy.orm import joinedload
from sqlmodel import col, delete, select, update

from common.crud import Crud
from recipes.models import Recipe, RecipeImage, RecipeIngredient


class RecipeCrud(Crud[Recipe]):
    model = Recipe

    def get_query(self):
        return (
            select(Recipe)
            .order_by(col(Recipe.id).desc())
            .options(joinedload(Recipe.images))
        )

    def get_details_query(self):
        return (
            select(Recipe)
            .options(joinedload(Recipe.images))
            .options(joinedload(Recipe.ingredients))
        )

    def filter_query(self, stmt, query: str | None):
        if not query:
            return stmt

        return stmt.where(col(Recipe.name).icontains(query))

    async def delete(self, instance: Recipe):
        await self.remove_images([image.id for image in instance.images])
        ingredients_stmt = delete(RecipeIngredient).where(
            RecipeIngredient.recipe_id == instance.id
        )
        await self.session.exec(ingredients_stmt)
        await self.session.commit()

        stmt = delete(Recipe).where(Recipe.id == instance.id)
        await self.session.exec(stmt)
        await self.session.commit()

    async def remove_ingredients(self, recipe: Recipe):
        stmt = delete(RecipeIngredient).where(RecipeIngredient.recipe_id == recipe.id)
        await self.session.exec(stmt)
        await self.session.commit()

    async def remove_images(self, images_ids: list[int]):
        stmt = delete(RecipeImage).where(RecipeImage.id.in_(images_ids))
        await self.session.exec(stmt)
        await self.session.commit()

    async def connect_recipe_with_images(
        self,
        recipe: Recipe,
        images_ids: list[int],
    ):
        stmt = (
            update(RecipeImage)
            .where(RecipeImage.id.in_(images_ids))
            .values(recipe_id=recipe.id)
        )
        await self.session.exec(stmt)
        await self.session.commit()
