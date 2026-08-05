from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_session
from app.database.schemas import ToDoAnalyticsFilterParams
from app.services.analytics_service import AnalyticsService, get_analytics_service


router = APIRouter(prefix="/todos/analytics", tags=["analytics"])


@router.get(
    "/",
    # dependencies=[manager_role_required],
)
async def get_todos_analytics(
    filter_params: Annotated[ToDoAnalyticsFilterParams, Depends()],
    session: AsyncSession = Depends(get_session),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    return await analytics_service.get_analytics(session=session, filter_params=filter_params)