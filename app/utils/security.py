import datetime as dt
from copy import deepcopy
from typing import Any

import bcrypt
import jwt
from fastapi.security import OAuth2PasswordBearer

from app.errors.exceptions import JWTExpiredTokenException, JWTInvalidTokenException
from app.utils.config import settings


oauth_scheme = OAuth2PasswordBearer(tokenUrl="login")


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
    def create_token(payload_data: dict[str, Any]) -> str:
        payload = deepcopy(payload_data)
        current_time = dt.datetime.now(dt.UTC)
        expire_time = current_time + dt.timedelta(seconds=settings.security.JWT_EXPIRE_SECONDS)
        payload.update({
            "exp": expire_time,
        })
        return jwt.encode(payload, settings.security.JWT_SECRET, algorithm="HS256")

    @staticmethod
    def decode_token(token: str) -> dict[str, Any]:
        try:
            return jwt.decode(token, settings.security.JWT_SECRET, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise JWTExpiredTokenException
        except jwt.InvalidTokenError:
            raise JWTInvalidTokenException
