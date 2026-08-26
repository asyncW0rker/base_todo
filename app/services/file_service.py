import asyncio
from dataclasses import dataclass
from typing import Any

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.errors.exceptions import FileFormatException
from app.errors.http_exceptions import HTTPNoFileProvidedException, HTTPFileFormatException
from app.repos.import_job_repo import ImportJobRepository
from app.utils.parsers.file_manager import FileManager


@dataclass
class FileService:
    file_manager: FileManager = FileManager()
    import_repo: ImportJobRepository = ImportJobRepository()

    async def import_todos_from_file(
        self,
        file: UploadFile,
        session: AsyncSession,
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
            session=session,
            job_id=job.id,
            filename=file.filename,
            file_content=file_content,
            user_id=job.user_id,
        ))

        return {"job_id": job.id}

    async def _process_import_job(
        self,
        session: AsyncSession,
        job_id: int,
        filename: str,
        file_content: bytes,
        user_id: int,
    ):
        pass

