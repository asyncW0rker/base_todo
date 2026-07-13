from typing import Sequence

from sqlalchemy import select, GenerativeSelect, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import ToDo
from app.database.schemas import ToDoSortingFields
from app.repos.base_repo import BaseRepository


class ToDoRepository(BaseRepository):
    model = ToDo

    async def get_many(
        self,
        session: AsyncSession,
        limit: int = 10,
        offset: int = 0,
        sort_by: ToDoSortingFields = ToDoSortingFields.CREATED_AT,
    ) -> Sequence[ToDo]:
        query = select(self.model).limit(limit).offset(offset)
        query = self._add_ordering_params(query, sort_by)
        result = await session.execute(query)
        return result.scalars().all()
