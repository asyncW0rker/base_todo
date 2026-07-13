from typing import Any

from sqlalchemy import select, Sequence, delete, update, GenerativeSelect, desc, Executable
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    model = None

    @staticmethod
    def _add_ordering_params(query: GenerativeSelect, sort_by: str) -> GenerativeSelect | Executable:
        if sort_by.startswith("-"):
            return query.order_by(desc(sort_by[1:]))
        return query.order_by(sort_by)

    async def create_one(self, session: AsyncSession, creation_data: dict[str, Any]) -> Any:
        new_object = self.model(**creation_data)
        session.add(new_object)
        await session.commit()
        await session.refresh(new_object)
        return new_object

    async def get_one(self, session: AsyncSession, item_id: int) -> Any:
        return await session.get(self.model, item_id)

    async def get_all(self, session: AsyncSession) -> Sequence[Any]:
        result = await session.execute(select(self.model))
        return result.scalars().all()

    async def update_one(self, session: AsyncSession, item_id: int, update_data: dict[str, Any]) -> int:
        result = await session.execute(update(self.model).where(self.model.id == item_id).values(**update_data))
        await session.commit()
        return result.rowcount

    async def delete_one(self, session: AsyncSession, item_id: int) -> int:
        result = await session.execute(delete(self.model).where(self.model.id == item_id))
        await session.commit()
        return result.rowcount

    async def delete_all(self, session: AsyncSession) -> None:
        await session.execute(delete(self.model))
        await session.commit()

