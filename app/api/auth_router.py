from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_session
from app.database.schemas import AuthData, RefreshToken, UserOutput, UserCreate, HTTPErrorDetail, AuthOutput, Message
from app.services.auth_service import AuthService, get_auth_service
from app.services.user_service import UserService, get_user_service
from app.utils.dependencies import admin_role_required


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserOutput,
    responses={
        status.HTTP_201_CREATED: {"model": UserOutput},
        status.HTTP_409_CONFLICT: {"model": HTTPErrorDetail},
    }
)
async def create_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.register_user(session, user_data)


@router.post(
    "/login",
    response_model=AuthOutput,
    responses={
        status.HTTP_200_OK: {"model": AuthOutput},
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPErrorDetail},
    }
)
async def authenticate_user(
    auth_data: AuthData,
    session: AsyncSession = Depends(get_session),
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.authenticate(session, auth_data)


@router.post(
    "/refresh",
    response_model=AuthOutput,
    responses={
        status.HTTP_200_OK: {"model": AuthOutput},
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPErrorDetail},
    }
)
async def refresh_token(
    refresh_data: RefreshToken,
    session: AsyncSession = Depends(get_session),
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.refresh(session, refresh_data)


@router.post(
    "/revoke/{user_id}",
    response_model=Message,
    responses={
        status.HTTP_200_OK: {"model": Message},
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPErrorDetail},
        status.HTTP_403_FORBIDDEN: {"model": HTTPErrorDetail},
        status.HTTP_404_NOT_FOUND: {"model": HTTPErrorDetail},
    },
    dependencies=[admin_role_required],
)
async def revoke_token(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.revoke_token(session, user_id)
