import bcrypt

from app.config import settings


class PasswordManager:
    DUMMY_HASH = bcrypt.hashpw(settings.DUMMY_HASH.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
