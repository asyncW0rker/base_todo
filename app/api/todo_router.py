from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_session
from app.database.schemas import ToDoCreate, ToDoUpdate, ToDoOutput, ToDoOrderingParams, ToDoFilterParams, \
    ToDoAnalyticsFilterParams, ToDoStatusUpdate, UserRole
from app.services.todo_service import ToDoService, get_todo_service
from app.utils.dependencies import admin_role_required, auth_required, user_ownership_required, manager_role_required
from app.utils.utils import get_current_user_payload


router = APIRouter(prefix="/todos", tags=["todos"])


@router.get(
    "/",
    response_model=list[ToDoOutput],
    # dependencies=[auth_required]
)
async def get_todos(
    ordering_params: Annotated[ToDoOrderingParams, Depends()],
    filter_params: Annotated[ToDoFilterParams, Depends()],
    # current_user_info: dict[str, Any] = Depends(get_current_user_payload),
    session: AsyncSession = Depends(get_session),
    todo_service: ToDoService = Depends(get_todo_service),
):
    return await todo_service.get_many_todos(
        session=session,
        ordering_params=ordering_params,
        filter_params=filter_params,
        # current_user_info=current_user_info,
        current_user_info={},
    )


@router.get(
    "/analytics",
    # dependencies=[manager_role_required],
)
async def get_todos_analytics(
    filter_params: Annotated[ToDoAnalyticsFilterParams, Depends()],
    session: AsyncSession = Depends(get_session),
    todo_service: ToDoService = Depends(get_todo_service),
):
    return await todo_service.get_analytics(session=session, filter_params=filter_params)


@router.get(
    "/{todo_id}",
    response_model=ToDoOutput,
    # dependencies=[auth_required],
)
async def get_todo(
    todo_id: int,
    # current_user_info: dict[str, Any] = Depends(get_current_user_payload),
    session: AsyncSession = Depends(get_session),
    todo_service: ToDoService = Depends(get_todo_service),
):
    return await todo_service.get_todo(session, todo_id, {})


@router.post(
    "/",
    response_model=ToDoOutput,
    # dependencies=[manager_role_required],
)
async def create_todo(
    todo_data: ToDoCreate,
    session: AsyncSession = Depends(get_session),
    todo_service: ToDoService = Depends(get_todo_service),
):
    return await todo_service.create_todo(session, todo_data)


@router.put(
    "/{todo_id}",
    # dependencies=[auth_required],
)
async def update_todo(
    todo_id: int,
    todo_data: ToDoUpdate,
    # current_user_info: dict[str, Any] = Depends(get_current_user_payload),
    session: AsyncSession = Depends(get_session),
    todo_service: ToDoService = Depends(get_todo_service),
):
    return await todo_service.update_todo(session, todo_id, todo_data, {})


@router.patch(
    "/",
    # dependencies=[auth_required],
)
async def update_status_for_todos(
    todo_data: ToDoStatusUpdate = Depends(),
    # current_user_info: dict[str, Any] = Depends(get_current_user_payload),
    session: AsyncSession = Depends(get_session),
    todo_service: ToDoService = Depends(get_todo_service),
):
    return await todo_service.update_status_for_todos(session, todo_data, {})


@router.delete(
    "/{todo_id}",
    # dependencies=[manager_role_required],
)
async def delete_todo(
    todo_id: int,
    session: AsyncSession = Depends(get_session),
    todo_service: ToDoService = Depends(get_todo_service),
):
    return await todo_service.delete_todo(session, todo_id)


@router.delete(
    "/",
    # dependencies=[admin_role_required],
)
async def delete_todos(
    session: AsyncSession = Depends(get_session),
    todo_service: ToDoService = Depends(get_todo_service),
):
    return await todo_service.delete_all_todos(session)