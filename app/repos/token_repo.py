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

    async def delete_by_user_id(self, session: AsyncSession, user_id: int) -> int:
        query = delete(self.model).where(self.model.user_id == user_id)
        result = await session.execute(query)
        await session.commit()
        return result.rowcount