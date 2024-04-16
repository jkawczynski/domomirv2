from sqlmodel import col, delete

from common.crud import Crud
from shopping.models import ShoppingListItem


class ShoppingListItemCrud(Crud[ShoppingListItem]):
    model = ShoppingListItem

    def get_query(self):
        return (
            super()
            .get_query()
            .order_by(
                col(ShoppingListItem.completed).desc(), col(ShoppingListItem.id).desc()
            )
        )

    async def delete_all_completed(self):
        stmt = delete(ShoppingListItem).where(
            col(ShoppingListItem.completed).is_not(None)
        )
        await self.session.exec(stmt)
        await self.session.commit()
