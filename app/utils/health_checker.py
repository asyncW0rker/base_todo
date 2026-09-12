import asyncio
from dataclasses import dataclass
from functools import lru_cache

from fastapi import status
from fastapi.responses import JSONResponse
import redis.asyncio as redis
from sqlalchemy import text

from app.database.db import get_db_context
from app.utils.config import settings
from app.utils.s3_manager import get_s3_manager


@dataclass
class HealthChecker:
    def __init__(self):
        self.redis_client = redis.from_url(
            url=settings.redis.redis_url,
            socket_connect_timeout=3,
            socket_timeout=3,
        )
        self.s3_manager = get_s3_manager()

    async def _check_database(self):
        async with get_db_context() as session:
            try:
                await session.execute(text("SELECT 1"))
                return {"status": "up"}
            except Exception as e:
                return {"status": "down", "error": str(e)}

    async def _check_redis(self):
        try:
            pong = await self.redis_client.ping()
            if pong:
                return {"status": "up"}
            return {"status": "down", "error": "Ping failed"}
        except Exception as e:
            return {"status": "down", "error": str(e)}

    async def _check_minio(self):
        return await self.s3_manager.check_health()

    async def check_health(self):
        try:
            db, broker, storage = await asyncio.wait_for(
                asyncio.gather(
                    self._check_database(),
                    self._check_redis(),
                    self._check_minio(),
                ),
                timeout=5,
            )
        except asyncio.TimeoutError:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "status": "unhealthy",
                    "error": "Health check timeout",
                },
            )

        healthy = all(service["status"] == "up" for service in (db, broker, storage))

        return JSONResponse(
            status_code=status.HTTP_200_OK if healthy else status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "healthy" if healthy else "unhealthy",
                "services": {
                    "postgres": db,
                    "redis": broker,
                    "minio_storage": storage,
                }
            }
        )


@lru_cache
def get_health_checker():
    return HealthChecker()
