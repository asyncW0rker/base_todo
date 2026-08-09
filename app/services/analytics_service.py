import datetime as dt
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.schemas import ToDoAnalyticsOutput, ToDoAnalyticsFilterParams
from app.errors.exceptions import TimezoneException, HTTPInvalidTimezoneException
from app.repos.analytics_job_repo import AnalyticsJobRepository
from app.repos.todo_repo import ToDoRepository


@dataclass
class AnalyticsService:
    todo_repo: ToDoRepository = ToDoRepository()
    analytics_repo: AnalyticsJobRepository = AnalyticsJobRepository()

    async def _get_weekday_analytics(
        self, session: AsyncSession, filter_params: dict[str, Any], timezone_str: str
    ) -> dict[str, int]:
        days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        weekday_map = dict(zip(range(7), days))
        weekday_distribution = {day: 0 for day in days}

        try:
            weekday_rows = await self.todo_repo.get_weekday_analytics(session, filter_params, timezone_str)
        except (TimezoneException, DBAPIError):
            raise HTTPInvalidTimezoneException

        for row in weekday_rows:
            day = weekday_map[row.weekday]
            weekday_distribution[day] = row.count

        return weekday_distribution

    async def _get_top_words_analytics(self, session: AsyncSession, filter_params: dict[str, Any]) -> dict[str, int]:
        top_words_result = await self.todo_repo.get_top_words_analytics(session, filter_params)
        top_words_analytics = {pair["word"]: pair["count"] for pair in top_words_result}
        return top_words_analytics

    async def compute_analytics(
        self, session: AsyncSession, filter_params: ToDoAnalyticsFilterParams
    ) -> ToDoAnalyticsOutput:
        filter_params = filter_params.model_dump()
        timezone = filter_params.pop("timezone", "Europe/Moscow")

        rows = await self.todo_repo.get_analytics(session, filter_params)

        total_count = rows[0].total_count if rows and rows[0].total_count else 0
        completed_count = rows[0].completed_count if rows and rows[0].completed_count else 0
        avg_completed = rows[0].average_completed if rows and rows[0].average_completed else dt.timedelta(seconds=0)
        avg_completion_time_hours = round(avg_completed.total_seconds() / 3600, 2)

        weekday_distribution = await self._get_weekday_analytics(session, filter_params, timezone)
        top_words_analytics = await self._get_top_words_analytics(session, filter_params)

        return ToDoAnalyticsOutput.model_validate({
            "total_count": total_count,
            "completed_stats": {
                "true": completed_count,
                "false": total_count - completed_count,
            },
            "avg_completion_time_hours": avg_completion_time_hours,
            "weekday_distribution": weekday_distribution,
            "top_words_in_titles": top_words_analytics,
        })


@lru_cache
def get_analytics_service() -> AnalyticsService:
    return AnalyticsService()
