from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any
from uuid import uuid4

from aiobotocore.session import get_session, AioSession
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Attachment
from app.database.schemas import AttachmentUploadRequest
from app.errors.exceptions import HTTPAttachmentTooLargeException, HTTPAttachmentNotFoundException, \
    HTTPToDoNotFoundException
from app.repos.attachment_repo import AttachmentRepository
from app.repos.todo_repo import ToDoRepository
from app.utils.config import settings
from app.utils.s3_manager import S3Manager


@dataclass
class AttachmentService:
    s3_manager: S3Manager = S3Manager()
    attachment_repo: AttachmentRepository = AttachmentRepository()
    todo_repo: ToDoRepository = ToDoRepository()

    async def get_all_attachments(self, session: AsyncSession) -> list[Attachment]:
        return await self.attachment_repo.get_all(session)

    async def request_upload(
        self,
        session: AsyncSession,
        todo_id: int,
        file_info: AttachmentUploadRequest,
    ):
        if file_info.size > settings.s3.S3_MAX_SIZE:
            raise HTTPAttachmentTooLargeException

        todo = await self.todo_repo.get_one(session, todo_id)
        if todo is None:
            raise HTTPToDoNotFoundException

        storage_key = self.s3_manager.generate_file_key(todo_id, file_info.filename)

        attachment_data = file_info.model_dump()
        attachment_data["storage_key"] = storage_key
        attachment_data["todo_id"] = todo_id

        await self.attachment_repo.create_one(session, attachment_data)

        upload_url = await self.s3_manager.generate_presigned_upload_url(
            file_key=storage_key,
            content_type=file_info.content_type,
            expires_in=300
        )

        return {
            "storage_key": storage_key,
            "upload_url": upload_url
        }

    async def delete_attachment(self, session: AsyncSession, attachment_id: int) -> dict[str, Any]:
        attachment = await self.attachment_repo.get_one(session, attachment_id)
        if attachment is None:
            raise HTTPAttachmentNotFoundException

        await self.s3_manager.delete_file(attachment.storage_key)
        await self.attachment_repo.delete_one(session, attachment_id)

        return {"message": "File deleted"}


@lru_cache
def get_attachment_service():
    return AttachmentService()
