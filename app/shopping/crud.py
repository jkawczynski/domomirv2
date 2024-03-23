from collections.abc import Sequence

from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from shopping.models import ShoppingListItem


async def get_list(session: AsyncSession) -> Sequence[ShoppingListItem]:
    stmt = select(ShoppingListItem).order_by(
        col(ShoppingListItem.completed).desc(), col(ShoppingListItem.id)
    )
    result = await session.exec(stmt)
    return result.all()


async def get_by_id(session: AsyncSession, item_id: int) -> ShoppingListItem | None:
    stmt = select(ShoppingListItem).where(ShoppingListItem.id == item_id)
    result = await session.exec(stmt)
    return result.first()


async def persist(session: AsyncSession, item: ShoppingListItem) -> ShoppingListItem:
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item
