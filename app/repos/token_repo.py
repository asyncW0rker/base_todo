from typing import Any

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Token
from app.repos.base_repo import BaseRepository


class TokenRepository(BaseRepository):
    model = Token

    async def get_one_by_hash(self, session: AsyncSession, item_hash: str) -> Any:
        query = select(self.model).where(self.model.refresh_token == item_hash)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def delete_one_uncommited(self, session: AsyncSession, item_id: int) -> Any:
        query = delete(self.model).where(self.model.id == item_id)
        await session.execute(query)