from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_session
from app.database.schemas import ToDoCreate, ToDoUpdate
from app.services.todo_service import ToDoService, get_todo_service

router = APIRouter(prefix="todos", tags=["todos"])


@router.get("/todos")
async def get_todos(
    session: AsyncSession = Depends(get_session),
    todo_service: ToDoService = Depends(get_todo_service),
):
    return await todo_service.get_all_todos(session)


@router.get("/todos/{todo_id}")
async def get_todos(
    todo_id: int,
    session: AsyncSession = Depends(get_session),
    todo_service: ToDoService = Depends(get_todo_service),
):
    return await todo_service.get_todo(session, todo_id)


@router.post("/todos")
async def create_todo(
    todo_data: ToDoCreate,
    session: AsyncSession = Depends(get_session),
    todo_service: ToDoService = Depends(get_todo_service),
):
    return await todo_service.create_todo(session, todo_data)


@router.put("/todos/{todo_id}")
async def update_todo(
    todo_id: int,
    todo_data: ToDoUpdate,
    session: AsyncSession = Depends(get_session),
    todo_service: ToDoService = Depends(get_todo_service),
):
    return await todo_service.update_todo(session, todo_id, todo_data)


@router.delete("/todos/{todo_id}")
async def delete_todo(
    todo_id: int,
    session: AsyncSession = Depends(get_session),
    todo_service: ToDoService = Depends(get_todo_service),
):
    return await todo_service.delete_todo(session, todo_id)