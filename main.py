from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.user_router import router as users_router
from app.api.todo_router import router as todos_router
from app.api.auth_router import router as auth_router
from app.api.analytics_router import router as analytics_router
from app.api.attachment_router import router as s3_router
from app.api.file_router import router as file_router
from app.api.monitoring_router import router as monitoring_router
from app.errors.handlers import pydantic_validation_exception_handler


app = FastAPI()

Instrumentator().instrument(app)

app.include_router(users_router)
app.include_router(auth_router)
app.include_router(todos_router)
app.include_router(analytics_router)
app.include_router(s3_router)
app.include_router(file_router)
app.include_router(monitoring_router)

app.add_exception_handler(RequestValidationError, pydantic_validation_exception_handler)
