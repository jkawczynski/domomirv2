from collections.abc import Sequence

from sqlmodel import col, select

from common.crud import Crud
from recipes.models import RecipeIngredient


class RecipeIngredientCrud(Crud[RecipeIngredient]):
    model = RecipeIngredient

    async def get_list_by_ids(
        self, ingredients_ids: list[int]
    ) -> Sequence[RecipeIngredient]:
        stmt = select(RecipeIngredient).where(
            col(RecipeIngredient.id).in_(ingredients_ids)
        )
        result = await self.session.exec(stmt)
        return result.all()
