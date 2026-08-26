import asyncio
from dataclasses import dataclass
from typing import Any

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import ImportJob
from app.database.schemas import JobStatus
from app.errors.exceptions import FileFormatException, FileNotFoundException
from app.errors.http_exceptions import HTTPNoFileProvidedException, HTTPFileFormatException, \
    HTTPImportJobNotFoundException
from app.repos.import_job_repo import ImportJobRepository
from app.repos.todo_repo import ToDoRepository
from app.utils.parsers.file_manager import FileManager


@dataclass
class FileService:
    file_manager: FileManager = FileManager()
    import_repo: ImportJobRepository = ImportJobRepository()
    todo_repo: ToDoRepository = ToDoRepository()

    async def get_import_job(self, session: AsyncSession, job_id: int) -> ImportJob:
        import_job = await self.import_repo.get_one(session, job_id)
        if import_job is None:
            raise HTTPImportJobNotFoundException
        return import_job

    async def update_import_job(self, session: AsyncSession, job_id: int, update_data: dict[str, Any]) -> ImportJob:
        job = await self.import_repo.update_one(session, job_id, dict(), update_data)
        if job is None:
            raise HTTPImportJobNotFoundException
        return job

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
        ))

        return {"job_id": job.id}

    async def _process_import_job(
        self,
        session: AsyncSession,
        job_id: int,
        filename: str,
        file_content: bytes,
    ):
        await self.update_import_job(session, job_id, {"status": JobStatus.RUNNING})

        try:
            parsed_rows = self.file_manager.parse_file(filename, file_content)
            errors = []
            created_count = 0

            for parsed_row in parsed_rows:
                if parsed_row.is_valid:
                    created_count += 1
                    await self.todo_repo.create_one_uncommited(session, parsed_row.data)
                else:
                    errors.append({
                        "row_number": parsed_row.row_number,
                        "error": parsed_row.error,
                        "data": parsed_row.data,
                     })

            await self.update_import_job(session, job_id, {
                "status": JobStatus.DONE,
                "created_count": created_count,
                "errors": errors,
            })

        except Exception as e:
            await self.update_import_job(session, job_id, {
                "status": JobStatus.FAILED,
                "errors": [{"error": f"Critical: {str(e)}"}],
            })

