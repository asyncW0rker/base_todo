from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_session
from app.database.schemas import ToDoCreate, ToDoUpdate, ToDoOutput, ToDoOrderingParams, ToDoFilterParams, \
    ToDoAnalyticsFilterParams, ToDoStatusUpdate
from app.services.todo_service import ToDoService, get_todo_service


router = APIRouter(prefix="/todos", tags=["todos"])


@router.get(
    "/",
    response_model=list[ToDoOutput],
)
async def get_todos(
    ordering_params: Annotated[ToDoOrderingParams, Depends()],
    filter_params: Annotated[ToDoFilterParams, Depends()],
    session: AsyncSession = Depends(get_session),
    todo_service: ToDoService = Depends(get_todo_service),
):
    return await todo_service.get_many_todos(
        session=session,
        ordering_params=ordering_params,
        filter_params=filter_params,
    )


@router.get("/analytics")
async def get_todos_analytics(
    filter_params: Annotated[ToDoAnalyticsFilterParams, Depends()],
    session: AsyncSession = Depends(get_session),
    todo_service: ToDoService = Depends(get_todo_service),
):
    return await todo_service.get_analytics(session=session, filter_params=filter_params)


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


@router.patch("/")
async def update_status_for_todos(
    todo_data: ToDoStatusUpdate = Depends(),
    session: AsyncSession = Depends(get_session),
    todo_service: ToDoService = Depends(get_todo_service),
):
    return await todo_service.update_status_for_todos(session, todo_data)


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