from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Sequence

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import ToDo
from app.database.schemas import ToDoOutput, JobStatus
from app.errors.exceptions import FileFormatException
from app.errors.http_exceptions import HTTPNoFileProvidedException, HTTPFileFormatException, \
    HTTPExportedFileNotFoundException
from app.services.file_service.file_service_base import FileServiceBase
from app.utils.background.tasks import process_import_job, process_export_job


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

        await process_import_job.kiq(
            job_id=job.id,
            filename=file.filename,
            file_content=file_content,
        )

        return {"job_id": job.id}

    async def export_todos_to_file(
        self,
        session: AsyncSession,
        todos: Sequence[ToDo],
        file_format: str,
        current_user_info: dict[str, Any],
    ):
        try:
            self.file_manager.get_handler_by_format(file_format)
        except FileFormatException:
            raise HTTPFileFormatException

        job = await self.export_repo.create_one(
            session=session,
            creation_data={
                "format": file_format,
                "user_id": int(current_user_info["sub"]),
                "records_count": len(todos),
            }
        )

        export_data = [
            ToDoOutput.model_validate(todo).model_dump(mode="json")
            for todo in todos
        ]

        await process_export_job.kiq(
            job_id=job.id,
            data=export_data,
        )

        return {"job_id": job.id}

    async def download_exported_data(self, session: AsyncSession, job_id: int):
        job = await self.get_export_job(session, job_id)
        if job.status != JobStatus.DONE:
            raise HTTPExportedFileNotFoundException
        download_url = await self.s3_manager.generate_presigned_download_url(job.file_path)
        return {
            "storage_key": job.file_path,
            "download_url": download_url,
        }


@lru_cache
def get_file_service() -> FileService:
    return FileService()
