from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.schemas import UserCreate, UserOutput
from app.services.user_service import UserService, get_user_service


router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/register",
    response_model=UserOutput,
)
async def create_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session),
    user_service: UserService = Depends(get_user_service)
):
    return await user_service.register_user(session, user_data)
