import datetime as dt
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User
from app.database.schemas import AuthData
from app.errors.exceptions import HTTPWrongCredentialsException, HTTPExpiredTokenException, HTTPInvalidTokenException
from app.repos.token_repo import TokenRepository
from app.repos.user_repo import UserRepository
from app.utils.config import settings
from app.utils.security import PasswordManager, JWTManager


@dataclass
class AuthService:
    user_repo: UserRepository = UserRepository()
    token_repo: TokenRepository = TokenRepository()
    password_manager: PasswordManager = PasswordManager()
    jwt_manager: JWTManager = JWTManager()

    async def _validate_user_data(self, session: AsyncSession, user_data: AuthData) -> User:
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

        return user

    async def _add_refresh_token_to_db(
        self,
        session: AsyncSession,
        refresh_token: str,
        user_id: int,
    ):
        refresh_hash = self.jwt_manager.hash_refresh_token(refresh_token)
        expires_at = dt.datetime.now(dt.UTC) + dt.timedelta(seconds=settings.security.JWT_REFRESH_EXPIRE_SECONDS)
        await self.token_repo.create_one(
            session=session,
            creation_data={
                "refresh_token": refresh_hash,
                "user_id": user_id,
                "expires_at": expires_at,
            }
        )

    async def authenticate(self, session: AsyncSession, user_data: AuthData):
        user = await self._validate_user_data(session, user_data)

        payload = {
            "sub": str(user.id),
        }
        access_token, refresh_token = self.jwt_manager.create_token_pair(payload)

        await self._add_refresh_token_to_db(session, refresh_token, user.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    async def refresh(self, session: AsyncSession, refresh_token: str):
        token_hash = self.jwt_manager.hash_refresh_token(refresh_token)
        token = await self.token_repo.get_one_by_hash(session, token_hash)
        if not token:
            raise HTTPInvalidTokenException

        current_time = dt.datetime.now(dt.UTC)
        if token.expires_at <= current_time:
            raise HTTPExpiredTokenException

        user_id, token_id = token.user_id, token.id
        payload = {
            "sub": str(user_id),
        }
        access_token, refresh_token = self.jwt_manager.create_token_pair(payload)

        await self.token_repo.delete_one_uncommited(session, token_id)
        await self._add_refresh_token_to_db(session, refresh_token, user_id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }


@lru_cache
def get_auth_service():
    return AuthService()
