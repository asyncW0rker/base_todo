from dataclasses import dataclass
from typing import Any

from functools import lru_cache
from sqlalchemy import Sequence
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User
from app.errors.http_exceptions import HTTPUserAlreadyExistsException, HTTPUserNotFoundException
from app.repos.user_repo import UserRepository
from app.database.schemas import UserCreate, UserUpdate
from app.utils.security import PasswordManager


@dataclass
class UserService:
    repo: UserRepository = UserRepository()
    password_manager: PasswordManager = PasswordManager()

    async def register_user(self, session: AsyncSession, creation_data: UserCreate) -> User:
        existed_user = await self.repo.get_one_by_username(session, creation_data.username)
        if existed_user is not None:
            raise HTTPUserAlreadyExistsException

        creation_data.password = self.password_manager.hash_password(creation_data.password)
        return await self.repo.create_one(session, creation_data.model_dump())

    async def get_user(self, session: AsyncSession, user_id: int) -> User | None:
        user = await self.repo.get_one_with_todos(session, user_id)
        if user is None:
            raise HTTPUserNotFoundException
        return user

    async def get_all_users(self, session: AsyncSession) -> Sequence[User]:
        return await self.repo.get_all_with_todos(session)

    async def update_user(self, session: AsyncSession, user_id: int, update_data: UserUpdate):
        try:
            update_data.password = self.password_manager.hash_password(update_data.password)
            changed_user = await self.repo.update_one(session, user_id, dict(), update_data.model_dump())
            if changed_user is None:
                raise HTTPUserNotFoundException
        except IntegrityError:
            raise HTTPUserAlreadyExistsException

        return {"message": "User updated"}

    async def delete_user(self, session: AsyncSession, user_id: int) -> dict:
        deleted_user = await self.repo.delete_one(session, user_id)
        if deleted_user == 0:
            raise HTTPUserNotFoundException
        return {"message": "User deleted"}

    async def delete_all_users(self, session: AsyncSession) -> dict[str, Any]:
        await self.repo.delete_all(session)
        return {"message": "All users deleted"}


@lru_cache
def get_user_service() -> UserService:
    return UserService()
