import datetime as dt
import hashlib
import secrets
from copy import deepcopy
from typing import Any

import bcrypt
import jwt
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPBasicCredentials

from app.errors.exceptions import JWTExpiredTokenException, JWTInvalidTokenException
from app.utils.config import settings


auth_scheme = HTTPBearer()


def get_token(credentials: HTTPBasicCredentials = Depends(auth_scheme)) -> str:
    return credentials.credentials


class PasswordManager:
    DUMMY_HASH = bcrypt.hashpw(settings.security.DUMMY_HASH.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


class JWTManager:
    @staticmethod
    def create_access_token(payload_data: dict[str, Any]) -> str:
        payload = deepcopy(payload_data)
        current_time = dt.datetime.now(dt.UTC)
        expire_time = current_time + dt.timedelta(seconds=settings.security.JWT_ACCESS_EXPIRE_SECONDS)
        payload.update({
            "exp": expire_time,
        })
        return jwt.encode(payload, settings.security.JWT_SECRET, algorithm="HS256")

    @staticmethod
    def create_refresh_token() -> str:
        return secrets.token_urlsafe(64)

    @staticmethod
    def hash_refresh_token(refresh_token: str) -> str:
        return hashlib.sha256(refresh_token.encode()).hexdigest()

    @classmethod
    def create_token_pair(cls, payload_data: dict[str, Any]) -> tuple[str, str]:
        access_token = cls.create_access_token(payload_data)
        refresh_token = cls.create_refresh_token()
        return access_token, refresh_token

    @staticmethod
    def decode_access_token(token: str) -> dict[str, Any]:
        try:
            return jwt.decode(token, settings.security.JWT_SECRET, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise JWTExpiredTokenException
        except jwt.InvalidTokenError:
            raise JWTInvalidTokenException
