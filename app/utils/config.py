from dataclasses import dataclass, field

from dotenv import find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=find_dotenv(), extra="ignore")

    DB_NAME: str
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: str

    @property
    def db_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


class SecuritySettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=find_dotenv(), extra="ignore")

    DUMMY_HASH: str
    JWT_SECRET: str
    JWT_EXPIRE_SECONDS: int


class Settings(BaseSettings):
    database: DatabaseSettings = DatabaseSettings()
    security: SecuritySettings = SecuritySettings()


settings = Settings()
