from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Attachment, ToDo
from app.database.schemas import AttachmentUploadRequest, UserRole
from app.errors.exceptions import HTTPAttachmentTooLargeException, HTTPAttachmentNotFoundException, \
    HTTPToDoNotFoundException, FileNotFoundException, TooLargeException, HTTPPrivatePermissionDeniedException
from app.repos.attachment_repo import AttachmentRepository
from app.repos.todo_repo import ToDoRepository
from app.utils.config import settings
from app.utils.s3_manager import S3Manager, get_s3_manager


@dataclass
class AttachmentService:
    s3_manager: S3Manager = field(default_factory=get_s3_manager)
    attachment_repo: AttachmentRepository = AttachmentRepository()
    todo_repo: ToDoRepository = ToDoRepository()

    @staticmethod
    def _check_user_permission(
        allowed_user_id: int,
        current_user_info: dict[str, Any],
    ):
        user_id, user_role = int(current_user_info.get("sub")), current_user_info.get("role")
        if user_role == UserRole.USER and user_id != allowed_user_id:
            raise HTTPPrivatePermissionDeniedException

    async def get_all_attachments(self, session: AsyncSession) -> list[Attachment]:
        return await self.attachment_repo.get_all(session)

    async def request_upload(
        self,
        session: AsyncSession,
        todo_id: int,
        file_info: AttachmentUploadRequest,
        current_user_info: dict[str, Any],
    ):
        if file_info.size > settings.s3.S3_MAX_SIZE:
            raise HTTPAttachmentTooLargeException

        todo = await self.todo_repo.get_one(session, todo_id)
        if todo is None:
            raise HTTPToDoNotFoundException

        self._check_user_permission(todo.user_id, current_user_info)

        storage_key = self.s3_manager.generate_file_key(todo_id, file_info.filename)

        attachment_data = {
            **file_info.model_dump(),
            "storage_key": storage_key,
            "todo_id": todo_id,
        }
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

    async def confirm_upload(self, session: AsyncSession, attachment_id: int):
        attachment = await self.attachment_repo.update_one(
            session=session,
            item_id=attachment_id,
            filter_params=dict(),
            update_data={"is_uploaded": True}
        )
        if attachment is None:
            raise HTTPAttachmentNotFoundException

        try:
            await self.s3_manager.verify_file_size(attachment.storage_key, settings.s3.S3_MAX_SIZE)
        except FileNotFoundException:
            raise HTTPAttachmentNotFoundException
        except TooLargeException:
            await self.s3_manager.delete_file(attachment.storage_key)
            await self.attachment_repo.delete_one(session, attachment_id)
            raise HTTPAttachmentTooLargeException

        return {"message": "Uploaded successfully"}

    async def download_attachment(self, session: AsyncSession, attachment_id: int):
        attachment = await self.attachment_repo.get_one(session, attachment_id)
        if attachment is None or not attachment.is_uploaded:
            raise HTTPAttachmentNotFoundException

        download_url = await self.s3_manager.generate_presigned_download_url(attachment.storage_key)

        return {
            "storage_key": attachment.storage_key,
            "download_url": download_url
        }

    async def delete_attachment(
        self,
        session: AsyncSession,
        attachment_id: int,
        current_user_info: dict[str, Any],
    ) -> dict[str, Any]:
        attachment = await self.attachment_repo.get_one_with_related_model(session, attachment_id)
        if attachment is None:
            raise HTTPAttachmentNotFoundException

        self._check_user_permission(attachment.todo.user_id, current_user_info)

        await self.s3_manager.delete_file(attachment.storage_key)
        await self.attachment_repo.delete_one(session, attachment_id)

        return {"message": "File deleted"}


@lru_cache
def get_attachment_service():
    return AttachmentService()
