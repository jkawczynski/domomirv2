from fastapi import Depends, HTTPException

from shopping import models
from shopping.crud import ShoppingListItemCrud


class ShoppingListItemService:
    def __init__(
        self, crud: ShoppingListItemCrud = Depends(ShoppingListItemCrud)
    ) -> None:
        self.crud = crud

    async def create_shopping_list_item(
        self,
        shopping_list_item: models.ShoppingListItemCreate,
    ):
        db_item = models.ShoppingListItem.model_validate(shopping_list_item)
        return await self.crud.persist(db_item)

    async def update_item(
        self,
        item_id: int,
        shopping_list_item: models.ShoppingListItemEdit,
    ):
        db_item = await self.crud.get_by_id(item_id)
        if not db_item:
            raise HTTPException(status_code=404, detail="Item not found")

        # TODO: figure out better way to do partial update
        db_item.completed = shopping_list_item.completed
        return await self.crud.persist(db_item)
