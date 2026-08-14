from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any
from uuid import uuid4

from aiobotocore.session import get_session

from app.database.schemas import AttachmentUploadRequest
from app.errors.exceptions import HTTPAttachmentTooLargeException, HTTPAttachmentUnsupportedMedia
from app.repos.attachment_repo import AttachmentRepository
from app.utils.config import settings


@dataclass
class S3Service:
    attachment_repo: AttachmentRepository = AttachmentRepository()
    _client: Any | None = None
    _session: Any = field(default_factory=get_session)
    endpoint_url: str = settings.s3.s3_url
    access_key_id: str = settings.s3.S3_USER
    secret_access_key: str = settings.s3.S3_PASSWORD
    region_name: str = "us-east-1"
    bucket_name: str = settings.s3.S3_BUCKET

    async def get_client(self):
        if self._client is None:
            self._client = await self._session.create_client(
                "s3",
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                region_name=self.region_name,
            )
        return self._client

    async def close_client(self):
        if self._client is not None:
            await self._client.__aexit__(None, None, None)
            self._client = None

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
        client = await self.get_client()
        return await client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": self.bucket_name,
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
        client = await self.get_client()
        return await client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": self.bucket_name,
                "Key": file_key
            },
            ExpiresIn=expires_in
        )

    async def delete_file(self, file_key: str) -> None:
        client = await self.get_client()
        await client.delete_object(
            Bucket=self.bucket_name,
            Key=file_key
        )

    async def request_upload(
        self,
        todo_id: int,
        file_info: AttachmentUploadRequest,
    ):
        if file_info.size > settings.s3.S3_MAX_SIZE:
            raise HTTPAttachmentTooLargeException

        storage_key = self.generate_file_key(todo_id, file_info.filename)


@lru_cache
def get_s3_service():
    return S3Service()
