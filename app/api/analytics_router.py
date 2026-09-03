from typing import Annotated, Any

from fastapi import APIRouter, Depends, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.database.db import get_session
from app.database.schemas import ToDoAnalyticsFilterParams, JobAccepted, AnalyticsJobOutput, \
    JobStatus, HTTPErrorDetail
from app.services.analytics_service import AnalyticsService, get_analytics_service
from app.utils.dependencies import auth_required, manager_role_required
from app.utils.utils import get_current_user_payload


router = APIRouter(prefix="/todos/analytics", tags=["analytics"])


@router.post(
    "/compute",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=JobAccepted,
    responses={
        status.HTTP_202_ACCEPTED: {"model": JobAccepted},
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPErrorDetail},
        status.HTTP_403_FORBIDDEN: {"model": HTTPErrorDetail},
    },
    dependencies=[manager_role_required],
)
async def compute_todos_analytics(
    filter_params: ToDoAnalyticsFilterParams,
    background_tasks: BackgroundTasks,
    current_user_info: dict[str, Any] = Depends(get_current_user_payload),
    session: AsyncSession = Depends(get_session),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    return await analytics_service.start_compute_analytics(
        session=session,
        filter_params=filter_params,
        background_tasks=background_tasks,
        current_user_info=current_user_info,
    )


@router.get(
    "/{job_id}",
    response_model=AnalyticsJobOutput,
    responses={
        status.HTTP_200_OK: {"model": AnalyticsJobOutput},
        status.HTTP_202_ACCEPTED: {"model": JobAccepted},
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPErrorDetail},
        status.HTTP_403_FORBIDDEN: {"model": HTTPErrorDetail},
        status.HTTP_404_NOT_FOUND: {"model": HTTPErrorDetail},
    },
    dependencies=[manager_role_required],
)
async def get_todos_analytics(
    job_id: int,
    session: AsyncSession = Depends(get_session),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    analytics_job = await analytics_service.get_analytics_job(session=session, job_id=job_id)
    if analytics_job.status != JobStatus.DONE:
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
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPErrorDetail},
        status.HTTP_403_FORBIDDEN: {"model": HTTPErrorDetail},
        status.HTTP_404_NOT_FOUND: {"model": HTTPErrorDetail},
    },
    dependencies=[manager_role_required],
)
async def get_todos_analytics_by_params(
    filter_params: Annotated[ToDoAnalyticsFilterParams, Depends()],
    session: AsyncSession = Depends(get_session),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    return await analytics_service.get_analytics_job_by_params(session=session, filter_params=filter_params)
