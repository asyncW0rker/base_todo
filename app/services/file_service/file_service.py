import asyncio
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.errors.exceptions import FileFormatException
from app.errors.http_exceptions import HTTPNoFileProvidedException, HTTPFileFormatException
from app.services.file_service.file_service_base import FileServiceBase


@dataclass
class FileService(FileServiceBase):
    async def import_todos_from_file(
        self,
        session: AsyncSession,
        file: UploadFile,
        current_user_info: dict[str, Any],
    ):
        if not file.filename:
            raise HTTPNoFileProvidedException

        try:
            self.file_manager.get_handler_by_extension(file.filename)
        except FileFormatException:
            raise HTTPFileFormatException

        job = await self.import_repo.create_one(
            session=session,
            creation_data={
                "filename": file.filename,
                "user_id": int(current_user_info["sub"]),
            }
        )
        file_content = await file.read()

        asyncio.create_task(self._process_import_job(
            job_id=job.id,
            filename=file.filename,
            file_content=file_content,
        ))

        return {"job_id": job.id}


@lru_cache
def get_file_service() -> FileService:
    return FileService()
