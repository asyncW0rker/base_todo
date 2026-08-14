from dataclasses import dataclass, Field
from typing import Any

from aiobotocore.session import get_session

from app.utils.config import settings


@dataclass
class S3Service:
    _client: Any | None = None
    _session: Any = Field(default_factory=get_session)
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


def get_s3_service():
    return S3Service()
