from typing import Any

import bcrypt
import jwt
from fastapi.security import OAuth2PasswordBearer

from app.utils.config import settings


oauth_scheme = OAuth2PasswordBearer(tokenUrl="login")


class PasswordManager:
    DUMMY_HASH = bcrypt.hashpw(settings.DUMMY_HASH.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


class JWTManager:
    def create_token(self, payload: dict[str, Any]) -> str:
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="SHA-256")

    def decode_token(self, token: str) -> dict[str, Any]:
        try:
            return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["SHA-256"])
        except jwt.InvalidTokenError:
            raise
        except jwt.ExpiredSignatureError:
            return None