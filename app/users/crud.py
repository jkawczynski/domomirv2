from sqlmodel import select

from common.crud import Crud
from users.models import User


class UserCrud(Crud[User]):
    model = User

    async def get_by_name(self, name: str) -> User | None:
        stmt = select(User).where(User.name == name)
        result = await self.session.exec(stmt)
        return result.first()
