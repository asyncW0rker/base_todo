from typing import Annotated

from fastapi import APIRouter, Depends, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.database.db import get_session
from app.database.schemas import ToDoAnalyticsFilterParams, AnalyticsJobAccepted, AnalyticsJobOutput, \
    AnalyticsJobStatus, HTTPErrorDetail
from app.services.analytics_service import AnalyticsService, get_analytics_service


router = APIRouter(prefix="/todos/analytics", tags=["analytics"])


@router.post(
    "/compute",
    status_code=status.HTTP_201_CREATED,
    response_model=AnalyticsJobAccepted,
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


@router.get(
    "/{job_id}",
    response_model=AnalyticsJobOutput,
    responses={
        status.HTTP_200_OK: {"model": AnalyticsJobOutput},
        status.HTTP_202_ACCEPTED: {"model": AnalyticsJobAccepted},
        status.HTTP_404_NOT_FOUND: {"model": HTTPErrorDetail},
    }
)
async def get_todos_analytics(
    job_id: int,
    session: AsyncSession = Depends(get_session),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    analytics_job = await analytics_service.get_analytics_job(session, job_id)
    if analytics_job.status != AnalyticsJobStatus.DONE:
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={
                "job_id": job_id,
                "status": analytics_job.status
            }
        )
    return analytics_job


@router.get(
    "/",
    response_model=AnalyticsJobOutput,
    responses={
        status.HTTP_200_OK: {"model": AnalyticsJobOutput},
        status.HTTP_404_NOT_FOUND: {"model": HTTPErrorDetail},
    }
)
async def get_todos_analytics_by_params(
    filter_params: Annotated[ToDoAnalyticsFilterParams, Depends()],
    session: AsyncSession = Depends(get_session),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    return await analytics_service.get_analytics_job_by_params(session, filter_params)
