from sqlmodel import col, select

from common.crud import Crud
from recipes.models import RecipeImage


class RecipeImageCrud(Crud[RecipeImage]):
    model = RecipeImage

    async def get_list_by_ids(
        self,
        images_ids: list[int],
    ) -> list[RecipeImage]:
        stmt = select(RecipeImage).where(col(RecipeImage.id).in_(images_ids))
        result = await self.session.exec(stmt)
        return list(result.all())
