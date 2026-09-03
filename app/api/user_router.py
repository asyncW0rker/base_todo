from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_session
from app.database.schemas import UserUpdate, UserWithTodos, HTTPErrorDetail, Message
from app.services.user_service import UserService, get_user_service
from app.utils.dependencies import admin_role_required, user_ownership_required


router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    response_model=list[UserWithTodos],
    responses={
        status.HTTP_200_OK: {"model": list[UserWithTodos]},
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPErrorDetail},
        status.HTTP_403_FORBIDDEN: {"model": HTTPErrorDetail},
    },
    dependencies=[admin_role_required],
)
async def get_users(
    session: AsyncSession = Depends(get_session),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.get_all_users(session=session)


@router.get(
    "/{user_id}",
    response_model=UserWithTodos,
    responses={
        status.HTTP_200_OK: {"model": UserWithTodos},
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPErrorDetail},
        status.HTTP_403_FORBIDDEN: {"model": HTTPErrorDetail},
        status.HTTP_404_NOT_FOUND: {"model": HTTPErrorDetail},
    },
    dependencies=[user_ownership_required]
)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.get_user(session=session, user_id=user_id)


@router.put(
    "/{user_id}",
    response_model=Message,
    responses={
        status.HTTP_200_OK: {"model": Message},
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPErrorDetail},
        status.HTTP_403_FORBIDDEN: {"model": HTTPErrorDetail},
        status.HTTP_404_NOT_FOUND: {"model": HTTPErrorDetail},
        status.HTTP_409_CONFLICT: {"model": HTTPErrorDetail},
    },
    dependencies=[user_ownership_required],
)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    session: AsyncSession = Depends(get_session),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.update_user(
        session=session,
        user_id=user_id,
        update_data=user_data,
    )


@router.delete(
    "/{user_id}",
    response_model=Message,
    responses={
        status.HTTP_200_OK: {"model": Message},
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPErrorDetail},
        status.HTTP_403_FORBIDDEN: {"model": HTTPErrorDetail},
        status.HTTP_404_NOT_FOUND: {"model": HTTPErrorDetail},
    },
    dependencies=[admin_role_required],
)
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.delete_user(session=session, user_id=user_id)
