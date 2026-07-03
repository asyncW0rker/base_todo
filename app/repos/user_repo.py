from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User
from app.repos.base_repo import BaseRepository


class UserRepository(BaseRepository):
    model = User

    async def get_one_by_username(self, session: AsyncSession, username: str) -> User | None:
        result = await session.execute(select(self.model).where(User.username == username))
        return result.scalar_one_or_none()

