from dataclasses import dataclass
from typing import Any

from functools import lru_cache
from fastapi import HTTPException
from sqlalchemy import Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User
from app.repos.user_repo import UserRepository
from app.database.schemas import UserCreate, UserUpdate
from app.utils.password_manager import PasswordManager


@dataclass
class UserService:
    repo: UserRepository = UserRepository()
    password_manager: PasswordManager = PasswordManager()

    async def register_user(self, session: AsyncSession, creation_data: UserCreate) -> User:
        existed_user = await self.repo.get_one_by_username(session, creation_data.username)
        if existed_user is not None:
            raise HTTPException(409, "User already exists")

        creation_data.password = self.password_manager.hash_password(creation_data.password)
        return await self.repo.create_one(session, creation_data.model_dump())

    async def get_user(self, session: AsyncSession, user_id: int) -> User:
        user = await self.repo.get_one(session, user_id)
        if user is None:
            raise HTTPException(404, "User not found")
        return user

    async def get_all_users(self, session: AsyncSession) -> Sequence[User]:
        return await self.repo.get_all(session)

    async def update_user(self, session: AsyncSession, user_id: int, update_data: UserUpdate):
        changed_user = await self.repo.update_one(session, user_id, update_data.model_dump())
        if changed_user == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User updated"}

    async def delete_user(self, session: AsyncSession, user_id: int) -> dict:
        deleted_user = await self.repo.delete_one(session, user_id)
        if deleted_user == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User deleted"}

    async def delete_all_users(self, session: AsyncSession) -> dict[str, Any]:
        await self.repo.delete_all(session)
        return {"message": "All users deleted"}


@lru_cache
def get_user_service() -> UserService:
    return UserService()
