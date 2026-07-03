from dataclasses import dataclass

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import ToDo
from app.database.schemas import ToDoCreate, ToDoUpdate
from app.repos.todo_repo import ToDoRepository


@dataclass
class ToDoService:
    repo: ToDoRepository = ToDoRepository()

    async def create_todo(self, session: AsyncSession, todo_data: ToDoCreate) -> ToDo:
        return await self.create_todo(session, todo_data.model_dump())

    async def get_todo(self, session: AsyncSession, todo_id: int) -> ToDo | None:
        todo = await self.repo.get_one_by_id(session, todo_id)
        if todo is None:
            raise HTTPException(status_code=404, detail="ToDo not found")
        return todo

    async def get_all_todos(self, session: AsyncSession):
        return await self.repo.get_all(session)

    async def update_todo(self, session: AsyncSession, todo_id: int, update_data: ToDoUpdate):
        changed_todo = await self.repo.update_one(session, todo_id, update_data.model_dump())
        if changed_todo == 0:
            raise HTTPException(status_code=404, detail="ToDo not found")
        return {"message": "ToDo updated"}

    async def delete_todo(self, session: AsyncSession, todo_id: int):
        deleted_todo = await self.repo.delete_one(session, todo_id)
        if deleted_todo == 0:
            raise HTTPException(status_code=404, detail="ToDo not found")
        return {"message": "ToDo deleted"}
