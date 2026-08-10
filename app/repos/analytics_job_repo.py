from typing import Any

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import AnalyticsJob
from app.repos.base_repo import BaseRepository


class AnalyticsJobRepository(BaseRepository):
    model = AnalyticsJob

    async def get_last_one_with_params(self, session: AsyncSession, filter_params: dict[str, Any]):
        query = select(self.model)
        filtered_query = self._add_filter_params(query, filter_params)
        sorted_query = filtered_query.order_by(desc("created_at"))
        result = await session.execute(sorted_query)
        return result.scalars().first()
