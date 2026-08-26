from typing import Any

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_session
from app.services.file_service import FileService, get_file_service
from app.utils.utils import get_current_user_payload


router = APIRouter(prefix="/todos", tags=["files"])


@router.get("/import/{job_id}")
async def get_import_job_info(
    job_id: int,
    session: AsyncSession = Depends(get_session),
    file_service: FileService = Depends(get_file_service),
):
    return await file_service.get_import_job(session, job_id)


@router.post("/import")
async def import_todos(
    file: UploadFile = File(...),
    current_user_info: dict[str, Any] = Depends(get_current_user_payload),
    session: AsyncSession = Depends(get_session),
    file_service: FileService = Depends(get_file_service),
):
    return await file_service.import_todos_from_file(session, file, current_user_info)
