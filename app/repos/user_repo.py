from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import User
from app.repos.base_repo import BaseRepository


class UserRepository(BaseRepository):
    model = User

    async def get_one_by_username(self, session: AsyncSession, username: str) -> User | None:
        result = await session.execute(select(self.model).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_one_with_todos(self, session: AsyncSession, user_id: int) -> User | None:
        query = (
            select(self.model)
            .where(self.model.id == user_id)
            .options(selectinload(self.model.todos))
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def get_all_with_todos(self, session: AsyncSession) -> Sequence[User]:
        query = select(self.model).options(selectinload(self.model.todos))
        result = await session.execute(query)
        return result.scalars().all()
