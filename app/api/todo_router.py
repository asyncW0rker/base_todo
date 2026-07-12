from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_session
from app.database.schemas import ToDoCreate, ToDoUpdate, ToDoOutput, ToDoFilterParams
from app.services.todo_service import ToDoService, get_todo_service


router = APIRouter(prefix="/todos", tags=["todos"])


@router.get(
    "/",
    response_model=list[ToDoOutput],
)
async def get_todos(
    filter_params: Annotated[ToDoFilterParams, Query()],
    session: AsyncSession = Depends(get_session),
    todo_service: ToDoService = Depends(get_todo_service),
):
    return await todo_service.get_many_todos(
        session=session,
        limit=filter_params.limit,
        offset=filter_params.offset
    )


@router.get(
    "/{todo_id}",
    response_model=ToDoOutput,
)
async def get_todo(
    todo_id: int,
    session: AsyncSession = Depends(get_session),
    todo_service: ToDoService = Depends(get_todo_service),
):
    return await todo_service.get_todo(session, todo_id)


@router.post(
    "/",
    response_model=ToDoOutput,
)
async def create_todo(
    todo_data: ToDoCreate,
    session: AsyncSession = Depends(get_session),
    todo_service: ToDoService = Depends(get_todo_service),
):
    return await todo_service.create_todo(session, todo_data)


@router.put("/{todo_id}")
async def update_todo(
    todo_id: int,
    todo_data: ToDoUpdate,
    session: AsyncSession = Depends(get_session),
    todo_service: ToDoService = Depends(get_todo_service),
):
    return await todo_service.update_todo(session, todo_id, todo_data)


@router.delete("/{todo_id}")
async def delete_todo(
    todo_id: int,
    session: AsyncSession = Depends(get_session),
    todo_service: ToDoService = Depends(get_todo_service),
):
    return await todo_service.delete_todo(session, todo_id)


@router.delete("/")
async def delete_todos(
    session: AsyncSession = Depends(get_session),
    todo_service: ToDoService = Depends(get_todo_service),
):
    return await todo_service.delete_all_todos(session)