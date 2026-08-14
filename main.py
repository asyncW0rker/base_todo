from contextlib import asynccontextmanager
from typing import AsyncIterator, AsyncGenerator

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.api.user_router import router as users_router
from app.api.todo_router import router as todos_router
from app.api.auth_router import router as auth_router
from app.api.analytics_router import router as analytics_router
from app.errors.handlers import pydantic_validation_exception_handler
from app.services.s3_service import get_s3_service


s3_service = get_s3_service()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    await s3_service.get_client()

    yield

    await s3_service.close()


app = FastAPI(lifespan=lifespan)

app.include_router(users_router)
app.include_router(auth_router)
app.include_router(todos_router)
app.include_router(analytics_router)

app.add_exception_handler(RequestValidationError, pydantic_validation_exception_handler)
