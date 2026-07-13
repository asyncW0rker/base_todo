from dataclasses import dataclass
from functools import lru_cache

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import ToDo
from app.database.schemas import ToDoCreate, ToDoUpdate, ToDoSortingFields
from app.repos.todo_repo import ToDoRepository
from app.repos.user_repo import UserRepository


@dataclass
class ToDoService:
    repo: ToDoRepository = ToDoRepository()
    user_repo: UserRepository = UserRepository()

    async def _check_user_existence(self, session: AsyncSession, user_id: int) -> None:
        user = await self.user_repo.get_one(session, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

    async def create_todo(self, session: AsyncSession, creation_data: ToDoCreate) -> ToDo:
        if creation_data.user_id is not None:
            await self._check_user_existence(session, creation_data.user_id)

        return await self.repo.create_one(session, creation_data.model_dump())

    async def get_todo(self, session: AsyncSession, todo_id: int) -> ToDo | None:
        todo = await self.repo.get_one(session, todo_id)
        if todo is None:
            raise HTTPException(status_code=404, detail="ToDo not found")
        return todo

    async def get_all_todos(self, session: AsyncSession):
        return await self.repo.get_all(session)

    async def get_many_todos(
        self,
        session: AsyncSession,
        limit: int,
        offset: int,
        sort_by: ToDoSortingFields,
    ):
        return await self.repo.get_many(session, limit, offset, sort_by)

    async def update_todo(self, session: AsyncSession, todo_id: int, update_data: ToDoUpdate):
        if update_data.user_id is not None:
            await self._check_user_existence(session, update_data.user_id)

        changed_todo = await self.repo.update_one(session, todo_id, update_data.model_dump())
        if changed_todo == 0:
            raise HTTPException(status_code=404, detail="ToDo not found")
        return {"message": "ToDo updated"}

    async def delete_todo(self, session: AsyncSession, todo_id: int):
        deleted_todo = await self.repo.delete_one(session, todo_id)
        if deleted_todo == 0:
            raise HTTPException(status_code=404, detail="ToDo not found")
        return {"message": "ToDo deleted"}

    async def delete_all_todos(self, session: AsyncSession):
        await self.repo.delete_all(session)
        return {"message": "All todos deleted"}


@lru_cache
def get_todo_service() -> ToDoService:
    return ToDoService()
