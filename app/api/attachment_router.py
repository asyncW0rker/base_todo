from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_session
from app.database.schemas import AttachmentUploadRequest
from app.services.attachment_service import AttachmentService, get_attachment_service


router = APIRouter(tags=["attachments"])


@router.get("/attachments/")
async def get_attachments(
    session: AsyncSession = Depends(get_session),
    attachment_service: AttachmentService = Depends(get_attachment_service),
):
    return await attachment_service.get_all_attachments(session)


@router.post("/todos/{todo_id}/attachments/request_upload")
async def create_attachment_request_upload(
    todo_id: int,
    file_data: AttachmentUploadRequest,
    session: AsyncSession = Depends(get_session),
    attachment_service: AttachmentService = Depends(get_attachment_service),
):
    return await attachment_service.request_upload(session, todo_id, file_data)


@router.post("/attachments/{attachment_id}/confirm")
async def confirm_upload_attachment(
    attachment_id: int,
    session: AsyncSession = Depends(get_session),
    attachment_service: AttachmentService = Depends(get_attachment_service),
):
    return await attachment_service.confirm_upload(session, attachment_id)


@router.get("/attachments/{attachment_id}/download")
async def download_attachment(
    attachment_id: int,
    session: AsyncSession = Depends(get_session),
    attachment_service: AttachmentService = Depends(get_attachment_service),
):
    return await attachment_service.download_attachment(session, attachment_id)


@router.delete("/attachments/{attachment_id}")
async def delete_attachment(
    attachment_id: int,
    session: AsyncSession = Depends(get_session),
    attachment_service: AttachmentService = Depends(get_attachment_service),
):
    return await attachment_service.delete_attachment(session, attachment_id)
