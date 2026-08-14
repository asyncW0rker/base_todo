from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.errors.exceptions import HTTPAttachmentUnsupportedMedia


async def pydantic_validation_exception_handler(request: Request, exc: RequestValidationError):
    for error in exc.errors():
        if "content_type" in error["loc"]:
            media_exc = HTTPAttachmentUnsupportedMedia()

            return JSONResponse(
                status_code=media_exc.status_code,
                content={"detail": media_exc.detail}
            )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )