from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.errors.http_exceptions import HTTPAttachmentUnsupportedMedia


async def pydantic_validation_exception_handler(request: Request, exc: RequestValidationError):
    for error in exc.errors():
        if "content_type" in error["loc"]:
            return JSONResponse(
                status_code= HTTPAttachmentUnsupportedMedia.status_code,
                content={"detail":  HTTPAttachmentUnsupportedMedia.detail}
            )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )
