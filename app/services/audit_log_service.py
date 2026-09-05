from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.repos.audit_log_repo import AuditLogRepository


@dataclass
class AuditLogService:
    logs_repo: AuditLogRepository = AuditLogRepository()

    async def get_logs(self, session: AsyncSession) -> list[dict[str, Any]]:
        return await self.logs_repo.get_all(session)


@lru_cache
def get_audit_log_service() -> AuditLogService:
    return AuditLogService()
