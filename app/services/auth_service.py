from dataclasses import dataclass
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.schemas import AuthData
from app.errors.exceptions import HTTPWrongCredentialsException
from app.repos.user_repo import UserRepository
from app.utils.security import PasswordManager, JWTManager


@dataclass
class AuthService:
    user_repo: UserRepository = UserRepository()
    password_manager: PasswordManager = PasswordManager()
    jwt_manager: JWTManager = JWTManager()

    async def authenticate(self, session: AsyncSession, user_data: AuthData):
        user = await self.user_repo.get_one_by_username(session, user_data.username)
        if user is None:
            self.password_manager.verify_password(user_data.password, self.password_manager.DUMMY_HASH)
            raise HTTPWrongCredentialsException

        is_correct_password = self.password_manager.verify_password(
            password=user_data.password,
            hashed_password=user.password
        )
        if not is_correct_password:
            raise HTTPWrongCredentialsException

        payload = {
            "sub": str(user.id),
        }
        token = self.jwt_manager.create_access_token(payload)
        return {
            "access_token": token,
        }


@lru_cache
def get_auth_service():
    return AuthService()
