from typing import Sequence, Any

import pytz
from sqlalchemy import select, GenerativeSelect, func, Executable, and_, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import ToDo
from app.database.schemas import ToDoSortingFields
from app.errors.exceptions import TimezoneException
from app.repos.base_repo import BaseRepository


class ToDoRepository(BaseRepository):
    model = ToDo

    def _add_filter_params(
        self, query: GenerativeSelect, filter_params: dict[str, Any],
    ) -> GenerativeSelect | Executable:
        completed = filter_params.pop("completed", None)
        title_contains = filter_params.pop("title_contains", None)
        created_after = filter_params.pop("created_after", None)
        created_before = filter_params.pop("created_before", None)

        filter_conditions = []
        if completed is not None:
            filter_conditions.append(self.model.completed == completed)
        if title_contains is not None:
            filter_conditions.append(self.model.title.icontains(title_contains))
        if created_after is not None:
            filter_conditions.append(self.model.created_at >= created_after)
        if created_before is not None:
            filter_conditions.append(self.model.created_at <= created_before)

        query = query.where(and_(*filter_conditions))

        return super()._add_filter_params(query, filter_params)

    def _add_search_params(
        self, query: GenerativeSelect, search_params: dict[str, Any],
    ) -> GenerativeSelect | Executable:
        search_query = search_params.get("q")
        language = search_params.get("language", "russian")
        if search_query is None:
            return query

        ts_query = func.plainto_tsquery(language, f"{search_query}:*")
        fts_match = self.model.search_vector.bool_op("@@")(ts_query)
        trgm_match = func.lower(self.model.title).ilike(f"%{search_query}%")

        combined_match = fts_match | trgm_match

        rank_expr = func.ts_rank_cd(self.model.search_vector, ts_query)
        query = (
            query
            .where(combined_match)
            .order_by(rank_expr.desc())
        )
        return query

    async def get_many(
        self,
        session: AsyncSession,
        filter_params: dict[str, Any],
        ordering_params: dict[str, Any],
        search_params: dict[str, Any],
    ) -> Sequence[ToDo]:
        limit, offset = ordering_params.get("limit", 10), ordering_params.get("offset", 0)
        sort_by = ordering_params.get("sort_by", ToDoSortingFields.CREATED_AT)

        query = select(self.model)
        search_query = self._add_search_params(query, search_params)
        filtered_query = self._add_filter_params(search_query, filter_params)
        limited_query = self._add_limit_and_offset(filtered_query, limit, offset)
        sorted_query = self._add_ordering_params(limited_query, sort_by)

        result = await session.execute(sorted_query)
        return result.scalars().all()

    async def get_weekday_analytics(
        self,
        session: AsyncSession,
        filter_params: dict[str, Any],
        timezone_str: str = "Europe/Moscow",
    ) -> Any:
        if timezone_str not in pytz.all_timezones:
            raise TimezoneException(f"Invalid timezone: {timezone_str}")

        weekday_expr = func.extract("dow", func.timezone(timezone_str, self.model.created_at)).label("weekday")
        weekday_query = (select(
            weekday_expr,
            func.count(self.model.id).label("count")
        ))

        weekday_query = self._add_filter_params(weekday_query, filter_params)
        weekday_query = weekday_query.group_by(weekday_expr)

        weekday_result = await session.execute(weekday_query)
        return weekday_result.all()

    async def get_analytics(self, session: AsyncSession, filter_params: dict[str, Any]) -> Any:
        query = select(
            func.count(self.model.id).label("total_count"),
            func.sum(
                case((self.model.completed == True, 1), else_=0)
            ).label("completed_count"),
            func.avg(
                case((
                    self.model.completed == True,
                    self.model.completed_at - self.model.created_at,
                ), else_=None)
            ).label("average_completed"),
        )
        query = self._add_filter_params(query, filter_params)
        result = await session.execute(query)
        return result.all()

    async def get_top_words_analytics(
        self,
        session: AsyncSession,
        filter_params: dict[str, Any],
        language: str = "russian",
        limit: int = 10,
    ) -> Any:
        lexeme_expr = func.unnest(
            func.tsvector_to_array(
                func.to_tsvector(language, func.coalesce(self.model.title, ""))
            )
        ).column_valued("word")

        query = (
            select(
                lexeme_expr.label("word"),
                func.count(lexeme_expr).label("count")
            )
            .select_from(self.model)
        )

        query = self._add_filter_params(query, filter_params)

        query = (
            query
            .group_by("word")
            .order_by(func.count(lexeme_expr).desc())
            .limit(limit)
        )

        result = await session.execute(query)
        return [dict(row) for row in result.mappings()]