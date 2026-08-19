from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.database.models import Attachment, ToDo
from app.repos.base_repo import BaseRepository


class AttachmentRepository(BaseRepository):
    model = Attachment

    async def get_one_with_related_model(self, session: AsyncSession, item_id: int):
        query = (
            select(self.model)
            .options(joinedload(self.model.todo))
            .where(self.model.id == item_id)
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()
