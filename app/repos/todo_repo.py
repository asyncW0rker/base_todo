from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import ToDo
from app.repos.base_repo import BaseRepository


class ToDoRepository(BaseRepository):
    model = ToDo

    async def get_many(self, session: AsyncSession, limit: int = 10, offset: int = 0):
        query = select(self.model).limit(limit).offset(offset)
        result = await session.execute(query)
        return result.scalars().all()
