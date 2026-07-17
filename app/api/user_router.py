from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_session
from app.database.schemas import UserCreate, UserOutput, UserUpdate, UserWithTodos
from app.services.user_service import UserService, get_user_service


router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    response_model=list[UserWithTodos],
)
async def get_users(
    session: AsyncSession = Depends(get_session),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.get_all_users(session)


@router.get(
    "/{user_id}",
    response_model=UserWithTodos,
)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.get_user(session, user_id)


@router.post(
    "/",
    response_model=UserOutput,
)
async def create_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.register_user(session, user_data)


@router.put("/{user_id}")
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    session: AsyncSession = Depends(get_session),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.update_user(session, user_id, user_data)


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.delete_user(session, user_id)


@router.delete("/")
async def delete_users(
    session: AsyncSession = Depends(get_session),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.delete_all_users(session)