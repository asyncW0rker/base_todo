from typing import Any, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import AuditLog
from app.database.schemas import AuditLogSortingFields
from app.repos.base_repo import BaseRepository


class AuditLogRepository(BaseRepository):
    model = AuditLog

    async def get_many(
        self,
        session: AsyncSession,
        filter_params: dict[str, Any],
        ordering_params: dict[str, Any],
    ) -> Sequence[Any]:
        limit, offset = ordering_params.get("limit", 10), ordering_params.get("offset", 0)
        sort_by = ordering_params.get("sort_by", AuditLogSortingFields.CREATED_AT)

        query = select(self.model)
        filtered_query = self._add_filter_params(query, filter_params)
        limited_query = self._add_limit_and_offset(filtered_query, limit, offset)
        sorted_query = self._add_ordering_params(limited_query, sort_by)

        result = await session.execute(sorted_query)
        return result.scalars().all()
