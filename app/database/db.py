from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.utils.config import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(settings.database.db_url)
session_maker = async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def get_db_context():
    async with session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_session():
    async with get_db_context() as session:
        yield session
