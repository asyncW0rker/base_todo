from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_session
from app.services.audit_log_service import AuditLogService, get_audit_log_service


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/audit")
async def get_logs(
    session: AsyncSession = Depends(get_session),
    log_service: AuditLogService = Depends(get_audit_log_service),
):
    return await log_service.get_logs(session)
