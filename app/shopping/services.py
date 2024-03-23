from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from shopping import crud, models


async def create_shopping_list_item(
    session: AsyncSession,
    shopping_list_item: models.ShoppingListItemCreate,
):
    db_item = models.ShoppingListItem.model_validate(shopping_list_item)
    return await crud.persist(session, db_item)


async def update_item(
    session: AsyncSession,
    item_id: int,
    shopping_list_item: models.ShoppingListItemEdit,
):
    db_item = await crud.get_by_id(session, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    # TODO: figure out better way to do partial update
    db_item.completed = shopping_list_item.completed
    return await crud.persist(session, db_item)
