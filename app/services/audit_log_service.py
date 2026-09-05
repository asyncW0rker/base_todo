from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.schemas import AuditLogOrderingParams, AuditLogFilterParams
from app.repos.audit_log_repo import AuditLogRepository


@dataclass
class AuditLogService:
    logs_repo: AuditLogRepository = AuditLogRepository()

    async def get_all_logs(self, session: AsyncSession) -> list[dict[str, Any]]:
        return await self.logs_repo.get_all(session)

    async def get_logs(
        self, session: AsyncSession, filter_params: AuditLogFilterParams, ordering_params: AuditLogOrderingParams,
    ) -> Sequence[Any]:
        return await self.logs_repo.get_many(
            session=session,
            filter_params=filter_params.model_dump(),
            ordering_params=ordering_params.model_dump(),
        )


@lru_cache
def get_audit_log_service() -> AuditLogService:
    return AuditLogService()
