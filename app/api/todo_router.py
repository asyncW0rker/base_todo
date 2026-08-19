from typing import Annotated, Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_session
from app.database.schemas import ToDoCreate, ToDoUpdate, ToDoOutput, ToDoOrderingParams, ToDoFilterParams, \
    ToDoStatusUpdate, ToDoPatch, ToDoSearchParams, HTTPErrorDetail, Message, ToDoWithAttachments
from app.services.todo_service import ToDoService, get_todo_service
from app.utils.dependencies import admin_role_required, auth_required, manager_role_required
from app.utils.utils import get_current_user_payload


router = APIRouter(prefix="/todos", tags=["todos"])


@router.get(
    "/",
    response_model=list[ToDoOutput],
    responses={
        status.HTTP_200_OK: {"model": list[ToDoOutput]},
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPErrorDetail},
        status.HTTP_403_FORBIDDEN: {"model": HTTPErrorDetail},
    },
    dependencies=[auth_required],
)
async def get_todos(
    ordering_params: Annotated[ToDoOrderingParams, Depends()],
    filter_params: Annotated[ToDoFilterParams, Depends()],
    search_params: Annotated[ToDoSearchParams, Depends()],
    current_user_info: dict[str, Any] = Depends(get_current_user_payload),
    session: AsyncSession = Depends(get_session),
    todo_service: ToDoService = Depends(get_todo_service),
):
    return await todo_service.get_many_todos(
        session=session,
        ordering_params=ordering_params,
        filter_params=filter_params,
        search_params=search_params,
        current_user_info=current_user_info,
    )


@router.get(
    "/{todo_id}",
    response_model=ToDoOutput,
    responses={
        status.HTTP_200_OK: {"model": ToDoOutput},
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPErrorDetail},
        status.HTTP_403_FORBIDDEN: {"model": HTTPErrorDetail},
        status.HTTP_404_NOT_FOUND: {"model": HTTPErrorDetail},
    },
    dependencies=[auth_required],
)
async def get_todo(
    todo_id: int,
    current_user_info: dict[str, Any] = Depends(get_current_user_payload),
    session: AsyncSession = Depends(get_session),
    todo_service: ToDoService = Depends(get_todo_service),
):
    return await todo_service.get_todo(session, todo_id, current_user_info)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ToDoWithAttachments,
    responses={
        status.HTTP_201_CREATED: {"model": ToDoWithAttachments},
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPErrorDetail},
        status.HTTP_403_FORBIDDEN: {"model": HTTPErrorDetail},
        status.HTTP_404_NOT_FOUND: {"model": HTTPErrorDetail},
    },
    dependencies=[manager_role_required],
)
async def create_todo(
    todo_data: ToDoCreate,
    session: AsyncSession = Depends(get_session),
    todo_service: ToDoService = Depends(get_todo_service),
):
    return await todo_service.create_todo(session, todo_data)


@router.put(
    "/{todo_id}",
    response_model=ToDoOutput,
    responses={
        status.HTTP_200_OK: {"model": ToDoOutput},
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPErrorDetail},
        status.HTTP_403_FORBIDDEN: {"model": HTTPErrorDetail},
        status.HTTP_404_NOT_FOUND: {"model": HTTPErrorDetail},
        status.HTTP_409_CONFLICT: {"model": HTTPErrorDetail},
    },
    dependencies=[auth_required],
)
async def update_todo(
    todo_id: int,
    todo_data: ToDoUpdate,
    current_user_info: dict[str, Any] = Depends(get_current_user_payload),
    session: AsyncSession = Depends(get_session),
    todo_service: ToDoService = Depends(get_todo_service),
):
    return await todo_service.update_todo(session, todo_id, todo_data, current_user_info)


@router.patch(
"/{todo_id}",
    response_model=ToDoOutput,
    responses={
        status.HTTP_200_OK: {"model": ToDoOutput},
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPErrorDetail},
        status.HTTP_403_FORBIDDEN: {"model": HTTPErrorDetail},
        status.HTTP_404_NOT_FOUND: {"model": HTTPErrorDetail},
        status.HTTP_409_CONFLICT: {"model": HTTPErrorDetail},
    },
    dependencies=[auth_required],
)
async def patch_todo(
    todo_id: int,
    todo_data: ToDoPatch,
    current_user_info: dict[str, Any] = Depends(get_current_user_payload),
    session: AsyncSession = Depends(get_session),
    todo_service: ToDoService = Depends(get_todo_service),
):
    return await todo_service.update_todo(session, todo_id, todo_data, current_user_info)


@router.patch(
    "/",
    response_model=Message,
    responses={
        status.HTTP_200_OK: {"model": Message},
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPErrorDetail},
        status.HTTP_403_FORBIDDEN: {"model": HTTPErrorDetail},
    },
    dependencies=[auth_required],
)
async def update_status_for_todos(
    todo_data: ToDoStatusUpdate = Depends(),
    current_user_info: dict[str, Any] = Depends(get_current_user_payload),
    session: AsyncSession = Depends(get_session),
    todo_service: ToDoService = Depends(get_todo_service),
):
    return await todo_service.update_status_for_todos(session, todo_data, current_user_info)


@router.delete(
    "/{todo_id}",
    response_model=Message,
    responses={
        status.HTTP_200_OK: {"model": Message},
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPErrorDetail},
        status.HTTP_403_FORBIDDEN: {"model": HTTPErrorDetail},
        status.HTTP_404_NOT_FOUND: {"model": HTTPErrorDetail},
    },
    dependencies=[manager_role_required],
)
async def delete_todo(
    todo_id: int,
    session: AsyncSession = Depends(get_session),
    todo_service: ToDoService = Depends(get_todo_service),
):
    return await todo_service.delete_todo(session, todo_id)


@router.delete(
    "/",
    response_model=Message,
    responses={
        status.HTTP_200_OK: {"model": Message},
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPErrorDetail},
        status.HTTP_403_FORBIDDEN: {"model": HTTPErrorDetail},
    },
    dependencies=[admin_role_required],
)
async def delete_todos(
    session: AsyncSession = Depends(get_session),
    todo_service: ToDoService = Depends(get_todo_service),
):
    return await todo_service.delete_all_todos(session)
