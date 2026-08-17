from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any
from uuid import uuid4

from aiobotocore.session import get_session, AioSession
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.schemas import AttachmentUploadRequest
from app.errors.exceptions import HTTPAttachmentTooLargeException, HTTPAttachmentNotFoundException, \
    HTTPToDoNotFoundException
from app.repos.attachment_repo import AttachmentRepository
from app.repos.todo_repo import ToDoRepository
from app.utils.config import settings


@dataclass
class S3Service:
    attachment_repo: AttachmentRepository = AttachmentRepository()
    todo_repo: ToDoRepository = ToDoRepository()
    _session: AioSession = field(default_factory=get_session)

    @staticmethod
    def _get_client_params():
        return {
            "service_name": "s3",
            "endpoint_url": settings.s3.s3_url,
            "aws_access_key_id": settings.s3.S3_USER,
            "aws_secret_access_key": settings.s3.S3_PASS,
            "region_name": "us-east-1",
        }

    @staticmethod
    def generate_file_key(todo_id: int, filename: str) -> str:
        extension = filename.split(".")[-1] if "." in filename else "bin"
        return f"todos/{todo_id}/attachments/{uuid4()}.{extension}"

    async def generate_presigned_upload_url(
        self,
        file_key: str,
        content_type: str,
        expires_in: int = 300
    ) -> str:
        async with self._session.create_client(**self._get_client_params()) as client:
            return await client.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": settings.s3.S3_BUCKET,
                    "Key": file_key,
                    "ContentType": content_type
                },
                ExpiresIn=expires_in,
                HttpMethod="PUT"
            )

    async def generate_presigned_download_url(
            self,
            file_key: str,
            expires_in: int = 3600
    ) -> str:
        async with self._session.create_client(**self._get_client_params()) as client:
            return await client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": settings.s3.S3_BUCKET,
                    "Key": file_key
                },
                ExpiresIn=expires_in
            )

    async def _delete_file_from_s3(self, file_key: str) -> None:
        async with self._session.create_client(**self._get_client_params()) as client:
            await client.delete_object(
                Bucket=settings.s3.S3_BUCKET,
                Key=file_key
            )

    async def delete_attachment(self, session: AsyncSession, attachment_id: int) -> dict[str, Any]:
        attachment = await self.attachment_repo.get_one(session, attachment_id)
        if attachment is None:
            raise HTTPAttachmentNotFoundException

        await self._delete_file_from_s3(attachment.storage_key)
        await self.attachment_repo.delete_one(session, attachment_id)

        return {"message": "File deleted"}

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

        storage_key = self.generate_file_key(todo_id, file_info.filename)

        attachment_data = file_info.model_dump()
        attachment_data["storage_key"] = storage_key
        attachment_data["todo_id"] = todo_id

        await self.attachment_repo.create_one(session, attachment_data)

        upload_url = await self.generate_presigned_upload_url(
            file_key=storage_key,
            content_type=file_info.content_type,
            expires_in=300
        )

        return {
            "storage_key": storage_key,
            "upload_url": upload_url
        }


@lru_cache
def get_s3_service():
    return S3Service()
