from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_session
from app.database.schemas import AuthData, RefreshToken, UserOutput, UserCreate
from app.services.auth_service import AuthService, get_auth_service
from app.services.user_service import UserService, get_user_service


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserOutput,
)
async def create_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.register_user(session, user_data)


@router.post("/login")
async def authenticate_user(
    auth_data: AuthData,
    session: AsyncSession = Depends(get_session),
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.authenticate(session, auth_data)


@router.post("/refresh")
async def refresh_token(
    refresh_data: RefreshToken,
    session: AsyncSession = Depends(get_session),
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.refresh(session, refresh_data)
