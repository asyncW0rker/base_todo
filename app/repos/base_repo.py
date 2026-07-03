from typing import Any

from sqlalchemy import select, Sequence, delete, update
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    model = None

    async def create_one(self, session: AsyncSession, creation_data: dict[str, Any]) -> Any:
        new_object = self.model(**creation_data)
        session.add(new_object)
        await session.commit()
        await session.refresh(new_object)
        return new_object

    async def get_all(self, session: AsyncSession) -> Sequence[Any]:
        result = await session.execute(select(self.model))
        return result.scalars().all()

    async def get_one(self, session: AsyncSession, id: int) -> Any:
        return await session.get(self.model, id)

    async def delete_all(self, session: AsyncSession) -> None:
        await session.execute(delete(self.model))
        await session.commit()

    async def update_one(self, session: AsyncSession, id: int, update_data: dict[str, Any]) -> int:
        result = await session.execute(update(self.model).where(self.model.id == id).values(**update_data))
        await session.commit()
        return result.rowcount
