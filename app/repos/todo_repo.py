from typing import Sequence, Any

from sqlalchemy import select, GenerativeSelect, desc, Executable, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import ToDo
from app.database.schemas import ToDoSortingFields
from app.repos.base_repo import BaseRepository


class ToDoRepository(BaseRepository):
    model = ToDo

    def _add_filter_params(
        self,
        query: GenerativeSelect,
        filter_params: dict[str, Any],
    ) -> GenerativeSelect | Executable:
        completed, title_contains = filter_params.get("completed"),  filter_params.get("title_contains")
        created_after, created_before = filter_params.get("created_after"), filter_params.get("created_before")
        filter_conditions = []

        if completed is not None:
            filter_conditions.append(self.model.completed == completed)
        if title_contains is not None:
            filter_conditions.append(self.model.title.contains(title_contains))
        if created_after is not None:
            filter_conditions.append(self.model.created_at >= created_after)
        if created_before is not None:
            filter_conditions.append(self.model.created_at <= created_before)

        return query.where(and_(*filter_conditions))

    async def get_many(
        self,
        session: AsyncSession,
        filter_params: dict[str, Any],
        limit: int = 10,
        offset: int = 0,
        sort_by: ToDoSortingFields = ToDoSortingFields.CREATED_AT,
    ) -> Sequence[ToDo]:
        query = select(self.model)
        filtered_query = self._add_filter_params(query, filter_params)
        limited_query = self._add_limit_and_offset(filtered_query, limit, offset)
        sorted_query = self._add_ordering_params(limited_query, sort_by)
        result = await session.execute(sorted_query)
        return result.scalars().all()
