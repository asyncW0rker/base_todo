from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.utils.config import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(settings.database.db_url)
session_maker = async_sessionmaker(engine)


async def get_session():
    async with session_maker() as session:
        yield session
