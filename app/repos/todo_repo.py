from typing import Sequence, Any
import datetime as dt

import pytz
from sqlalchemy import select, GenerativeSelect, func, Executable, and_, case, cast, String, text, ClauseElement, desc
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.compiler import compiles

from app.database.models import ToDo
from app.database.schemas import ToDoSortingFields
from app.errors.exceptions import TimezoneException
from app.repos.base_repo import BaseRepository


class explain(Executable, ClauseElement):
    inherit_cache = False

    def __init__(self, stmt, analyze=False):
        self.statement = stmt
        self.analyze = analyze


@compiles(explain, "postgresql")
def pg_explain(element, compiler, **kw):
    text = "EXPLAIN "
    if element.analyze:
        text += "ANALYZE "
    text += compiler.process(element.statement, **kw)

    return text


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
            .where(
                combined_match,
            )
            .order_by(
                rank_expr.desc()
            )
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

    async def _get_weekday_analytics(self, session: AsyncSession, timezone_str: str) -> dict[str, int]:
        if timezone_str not in pytz.all_timezones:
            raise TimezoneException(f"Invalid timezone: {timezone_str}")

        weekday_map = {
            0: "Sunday",
            1: "Monday",
            2: "Tuesday",
            3: "Wednesday",
            4: "Thursday",
            5: "Friday",
            6: "Saturday"
        }
        weekday_distribution = {day: 0 for day in weekday_map.values()}

        weekday_expr = func.extract("dow", func.timezone(timezone_str, self.model.created_at)).label("weekday")
        weekday_query = select(
            weekday_expr,
            func.count(self.model.id).label("count")
        ).group_by(weekday_expr)

        weekday_result = await session.execute(weekday_query)
        weekday_rows = weekday_result.all()
        for row in weekday_rows:
            day = weekday_map[row.weekday]
            weekday_distribution[day] = row.count

        return weekday_distribution

    async def get_analytics(
        self,
        session: AsyncSession,
        timezone_str: str = "Europe/Moscow",
    ) -> dict[str, Any]:
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

        result = await session.execute(query)
        rows = result.all()

        total_count = rows[0].total_count if rows and rows[0].total_count else 0
        completed_count = rows[0].completed_count if rows and rows[0].completed_count else 0
        average_completed = rows[0].average_completed if rows and rows[0].average_completed else dt.timedelta(seconds=0)
        avg_completion_time_hours = round(average_completed.total_seconds() / 3600, 2)

        try:
            weekday_distribution = await self._get_weekday_analytics(session, timezone_str)
        except DBAPIError:
            raise TimezoneException

        return {
            "total_count": total_count,
            "completed_stats": {
                "true": completed_count,
                "false": total_count - completed_count,
            },
            "avg_completion_time_hours": avg_completion_time_hours,
            "weekday_distribution": weekday_distribution,
        }
