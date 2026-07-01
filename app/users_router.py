from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import User
from app.schemas import UserCreate

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register")
async def create_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session)
):
    new_user = User(**user_data.model_dump())
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user

