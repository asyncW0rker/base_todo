from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.schemas import LogAction
from app.repos.audit_log_repo import AuditLogRepository


@dataclass
class LogManager:
    repo: AuditLogRepository = AuditLogRepository()

    async def log_create(
        self, session: AsyncSession, creation_data: dict[str, Any], actor_id: int, todo_id: int | None = None
    ) -> None:
        await self.repo.create_one_uncommited(session, {
            "actor_id": actor_id,
            "todo_id": todo_id,
            "action": LogAction.CREATE,
            "diff": {"created": creation_data}
        })

    async def log_update(
        self, session: AsyncSession, update_data: dict[str, Any], actor_id: int, todo_id: int
    ) -> None:
        await self.repo.create_one(session, {
            "actor_id": actor_id,
            "todo_id": todo_id,
            "action": LogAction.UPDATE,
            "diff": {"updated": update_data}
        })

    async def log_delete(self, session: AsyncSession, actor_id: int, todo_id: int) -> None:
        await self.repo.create_one(session, {
            "actor_id": actor_id,
            "todo_id": todo_id,
            "action": LogAction.DELETE,
            "diff": {"deleted": todo_id}
        })


@lru_cache
def get_log_manager():
    return LogManager()
