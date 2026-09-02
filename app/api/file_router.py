from typing import Any, Annotated

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_session
from app.database.schemas import ToDoFilterParams, ToDoSearchParams, ToDoExportOrderingParams
from app.services.file_service.file_service import FileService, get_file_service
from app.services.todo_service import ToDoService, get_todo_service
from app.utils.dependencies import auth_required
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


@router.get("/export/{job_id}")
async def get_export_job_info(
    job_id: int,
    session: AsyncSession = Depends(get_session),
    file_service: FileService = Depends(get_file_service),
):
    return await file_service.get_export_job(session, job_id)


@router.post(
    "/export",
    dependencies=[auth_required],
)
async def export_todos(
    file_format: str,
    ordering_params: Annotated[ToDoExportOrderingParams, Depends()],
    filter_params: Annotated[ToDoFilterParams, Depends()],
    current_user_info: dict[str, Any] = Depends(get_current_user_payload),
    session: AsyncSession = Depends(get_session),
    todo_service: ToDoService = Depends(get_todo_service),
    file_service: FileService = Depends(get_file_service),
):
    todos = await todo_service.get_many_todos(
        session=session,
        ordering_params=ordering_params,
        filter_params=filter_params,
        search_params=None,
        current_user_info=current_user_info,
    )
    return await file_service.export_todos_to_file(session, todos, file_format, current_user_info)
