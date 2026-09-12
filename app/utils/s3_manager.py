from dataclasses import dataclass, field
from functools import lru_cache
from uuid import uuid4

from aiobotocore.session import AioSession, get_session
from botocore.config import Config
from botocore.exceptions import ClientError

from app.errors.exceptions import TooLargeException, FileNotFoundException
from app.utils.config import settings


@dataclass
class S3Manager:
    _session: AioSession = field(default_factory=get_session)
    _S3_HEALTHCHECK_CONFIG: Config = Config(
        connect_timeout=2,
        read_timeout=3,
        retries={"max_attempts": 0},
    )
    _S3_WORK_CONFIG: Config = Config(
        connect_timeout=10,
        read_timeout=60,
        retries={"max_attempts": 3},
    )

    @staticmethod
    def _get_client_params(config: Config | None = None) -> dict:
        params = {
            "service_name": "s3",
            "endpoint_url": settings.s3.s3_url,
            "aws_access_key_id": settings.s3.S3_USER,
            "aws_secret_access_key": settings.s3.S3_PASS,
            "region_name": "us-east-1",
        }

        if config is not None:
            params["config"] = config

        return params

    @staticmethod
    def generate_file_key_for_attachments(todo_id: int, filename: str) -> str:
        extension = filename.split(".")[-1] if "." in filename else "bin"
        return f"todos/{todo_id}/attachments/{uuid4()}.{extension}"

    @staticmethod
    def generate_file_key_for_exports(user_id: int, filename: str) -> str:
        return f"exports/{user_id}/{filename}"

    async def generate_presigned_upload_url(self, file_key: str, content_type: str, expires_in: int = 300) -> str:
        async with self._session.create_client(**self._get_client_params(self._S3_WORK_CONFIG)) as client:
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
        async with self._session.create_client(**self._get_client_params(self._S3_WORK_CONFIG)) as client:
            return await client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": settings.s3.S3_BUCKET,
                    "Key": file_key
                },
                ExpiresIn=expires_in
            )

    async def upload_bytes(
        self,
        file_key: str,
        data: bytes,
        content_type: str,
    ) -> None:
        async with self._session.create_client(**self._get_client_params(self._S3_WORK_CONFIG)) as client:
            await client.put_object(
                Bucket=settings.s3.S3_BUCKET,
                Key=file_key,
                Body=data,
                ContentType=content_type,
            )

    async def verify_file_size(self, file_key: str, max_size: int):
        async with self._session.create_client(**self._get_client_params(self._S3_WORK_CONFIG)) as client:
            try:
                response = await client.head_object(Bucket=settings.s3.S3_BUCKET, Key=file_key)
                file_size = response["ContentLength"]
                if file_size > max_size:
                    raise TooLargeException(f"File has {file_size} bytes but is too large, max is {max_size}")
            except (client.exceptions.NoSuchKey, ClientError):
                raise FileNotFoundException("File not found")

    async def delete_file(self, file_key: str) -> None:
        async with self._session.create_client(**self._get_client_params(self._S3_WORK_CONFIG)) as client:
            await client.delete_object(
                Bucket=settings.s3.S3_BUCKET,
                Key=file_key
            )

    async def check_health(self):
        try:
            async with self._session.create_client(**self._get_client_params(self._S3_HEALTHCHECK_CONFIG)) as client:
                await client.list_buckets()
                return {"status": "up"}
        except Exception as e:
            return {"status": "down", "error": str(e)}


@lru_cache
def get_s3_manager():
    return S3Manager()
