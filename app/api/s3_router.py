from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_session
from app.database.schemas import AttachmentUploadRequest
from app.services import s3_service
from app.services.s3_service import S3Service, get_s3_service


router = APIRouter(tags=["attachments"])


@router.post("/todos/{todo_id}/attachments/request_upload")
async def create_attachment_request_upload(
    todo_id: int,
    file_data: AttachmentUploadRequest,
    session: AsyncSession = Depends(get_session),
    s3_service: S3Service = Depends(get_s3_service),
):
    return await s3_service.request_upload(session, todo_id, file_data)


@router.delete("/attachments/{attachment_id}")
async def delete_attachment(
    attachment_id: int,
    session: AsyncSession = Depends(get_session),
    s3_service: S3Service = Depends(get_s3_service),
):
    return await s3_service.delete_attachment(session, attachment_id)


@router.get("/attachments/")
async def get_attachments(
    session: AsyncSession = Depends(get_session),
    s3_service: S3Service = Depends(get_s3_service),
):
    return await s3_service.get_all_attachments(session)
