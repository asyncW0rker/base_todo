from typing import Annotated

from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_session
from app.database.schemas import ToDoAnalyticsFilterParams
from app.services import analytics_service
from app.services.analytics_service import AnalyticsService, get_analytics_service


router = APIRouter(prefix="/todos/analytics", tags=["analytics"])


@router.post(
    "/compute",
    # dependencies=[manager_role_required],
)
async def compute_todos_analytics(
    filter_params: ToDoAnalyticsFilterParams,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    return await analytics_service.start_compute_analytics(
        session=session, filter_params=filter_params, background_tasks=background_tasks
    )


@router.get("/{job_id}")
async def get_todos_analytics(
    job_id: int,
    session: AsyncSession = Depends(get_session),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    return await analytics_service.get_analytics_job(session, job_id)
