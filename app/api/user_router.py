from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_session
from app.database.schemas import UserUpdate, UserWithTodos
from app.services.user_service import UserService, get_user_service
from app.utils.rbac import admin_role_required, user_ownership_required


router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    response_model=list[UserWithTodos],
    dependencies=[admin_role_required],
)
async def get_users(
    session: AsyncSession = Depends(get_session),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.get_all_users(session)


@router.get(
    "/{user_id}",
    response_model=UserWithTodos,
    dependencies=[user_ownership_required]
)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.get_user(session, user_id)


@router.put(
    "/{user_id}",
    dependencies=[user_ownership_required],
)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    session: AsyncSession = Depends(get_session),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.update_user(session, user_id, user_data)


@router.delete(
    "/{user_id}",
    dependencies=[admin_role_required],
)
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.delete_user(session, user_id)


@router.delete(
    "/",
    dependencies=[admin_role_required],
)
async def delete_users(
    session: AsyncSession = Depends(get_session),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.delete_all_users(session)
