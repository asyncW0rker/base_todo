from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_session
from app.database.schemas import AttachmentUploadRequest, Message, HTTPErrorDetail, AttachmentOutput, \
    AttachmentUploadURL, AttachmentDownloadURL
from app.services.attachment_service import AttachmentService, get_attachment_service


router = APIRouter(tags=["attachments"])


@router.get(
    "/attachments/",
    response_model=list[AttachmentOutput],
)
async def get_attachments(
    session: AsyncSession = Depends(get_session),
    attachment_service: AttachmentService = Depends(get_attachment_service),
):
    return await attachment_service.get_all_attachments(session)


@router.post(
    "/todos/{todo_id}/attachments/request_upload",
    response_model=AttachmentUploadURL,
    responses={
        status.HTTP_200_OK: {"model": AttachmentUploadURL},
        status.HTTP_404_NOT_FOUND: {"model": HTTPErrorDetail},
        status.HTTP_413_CONTENT_TOO_LARGE: {"model": HTTPErrorDetail},
    }
)
async def create_attachment_request_upload(
    todo_id: int,
    file_data: AttachmentUploadRequest,
    session: AsyncSession = Depends(get_session),
    attachment_service: AttachmentService = Depends(get_attachment_service),
):
    return await attachment_service.request_upload(session, todo_id, file_data)


@router.post(
    "/attachments/{attachment_id}/confirm",
    response_model=Message,
    responses={
        status.HTTP_200_OK: {"model": Message},
        status.HTTP_404_NOT_FOUND: {"model": HTTPErrorDetail},
        status.HTTP_413_CONTENT_TOO_LARGE: {"model": HTTPErrorDetail},
    }
)
async def confirm_upload_attachment(
    attachment_id: int,
    session: AsyncSession = Depends(get_session),
    attachment_service: AttachmentService = Depends(get_attachment_service),
):
    return await attachment_service.confirm_upload(session, attachment_id)


@router.get(
    "/attachments/{attachment_id}/download",
    response_model=AttachmentDownloadURL,
    responses={
        status.HTTP_200_OK: {"model": AttachmentDownloadURL},
        status.HTTP_404_NOT_FOUND: {"model": HTTPErrorDetail},
    }
)
async def download_attachment(
    attachment_id: int,
    session: AsyncSession = Depends(get_session),
    attachment_service: AttachmentService = Depends(get_attachment_service),
):
    return await attachment_service.download_attachment(session, attachment_id)


@router.delete(
    "/attachments/{attachment_id}",
    response_model=Message,
    responses={
        status.HTTP_200_OK: {"model": Message},
        status.HTTP_404_NOT_FOUND: {"model": HTTPErrorDetail},
    }
)
async def delete_attachment(
    attachment_id: int,
    session: AsyncSession = Depends(get_session),
    attachment_service: AttachmentService = Depends(get_attachment_service),
):
    return await attachment_service.delete_attachment(session, attachment_id)
