from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_session
from app.database.schemas import AuditLogFilterParams, AuditLogOrderingParams, HTTPErrorDetail, Message, AuditLogOutput, \
    HealthOutput, HealthError
from app.services.audit_log_service import AuditLogService, get_audit_log_service
from app.utils.dependencies import admin_role_required
from app.utils.health_checker import HealthChecker, get_health_checker


router = APIRouter(tags=["monitoring"])


@router.get(
    "/admin/audit",
    dependencies=[admin_role_required],
    response_model=list[AuditLogOutput],
    responses={
        status.HTTP_200_OK: {"model": list[AuditLogOutput]},
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPErrorDetail},
        status.HTTP_403_FORBIDDEN: {"model": HTTPErrorDetail},
    },
)
async def get_logs(
    session: AsyncSession = Depends(get_session),
    log_service: AuditLogService = Depends(get_audit_log_service),
    filter_params: AuditLogFilterParams = Depends(),
    ordering_params: AuditLogOrderingParams = Depends(),
):
    return await log_service.get_logs(session, filter_params, ordering_params)


@router.get(
    "/health",
    response_model=HealthOutput,
    responses={
        status.HTTP_200_OK: {"model": HealthOutput},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": HealthOutput | HealthError},
    }
)
async def check_health(
    health_checker: HealthChecker = Depends(get_health_checker)
):
    return await health_checker.check_health()
