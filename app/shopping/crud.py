from collections.abc import Iterable, Sequence

from sqlmodel import col, delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from shopping.models import ShoppingListItem


async def get_list(session: AsyncSession) -> Sequence[ShoppingListItem]:
    stmt = select(ShoppingListItem).order_by(
        col(ShoppingListItem.completed).desc(), col(ShoppingListItem.id).desc()
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


async def persist_all(session: AsyncSession, items: Iterable[ShoppingListItem]):
    for item in items:
        session.add(item)

    await session.commit()


async def remove_all_completed(session: AsyncSession):
    stmt = delete(ShoppingListItem).where(col(ShoppingListItem.completed).is_not(None))
    await session.exec(stmt)
    await session.commit()
