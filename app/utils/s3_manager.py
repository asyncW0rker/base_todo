from dataclasses import dataclass, field
from uuid import uuid4

from aiobotocore.session import AioSession, get_session

from app.errors.exceptions import TooLargeException, FileNotFoundException
from app.utils.config import settings


@dataclass
class S3Manager:
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

    async def generate_presigned_upload_url(self, file_key: str, content_type: str, expires_in: int = 300) -> str:
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

    async def generate_presigned_download_url(self, file_key: str, expires_in: int = 3600) -> str:
        async with self._session.create_client(**self._get_client_params()) as client:
            return await client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": settings.s3.S3_BUCKET,
                    "Key": file_key
                },
                ExpiresIn=expires_in
            )

    async def verify_file_size(self, file_key: str, max_size: int):
        async with self._session.create_client(**self._get_client_params()) as client:
            try:
                response = await client.head_object(Bucket=settings.s3.S3_BUCKET, Key=file_key)
                file_size = response["ContentLength"]
                if file_size > max_size:
                    raise TooLargeException(f"File has {file_size} bytes but is too large, max is {max_size}")
            except client.exceptions.NoSuchKey:
                raise FileNotFoundException("File not found")

    async def delete_file(self, file_key: str) -> None:
        async with self._session.create_client(**self._get_client_params()) as client:
            await client.delete_object(
                Bucket=settings.s3.S3_BUCKET,
                Key=file_key
            )
