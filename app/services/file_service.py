import asyncio
import datetime as dt
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import session_maker
from app.database.models import ImportJob
from app.database.schemas import JobStatus, ParsedRow
from app.errors.exceptions import FileFormatException
from app.errors.http_exceptions import HTTPNoFileProvidedException, HTTPFileFormatException, \
    HTTPImportJobNotFoundException
from app.repos.import_job_repo import ImportJobRepository
from app.repos.todo_repo import ToDoRepository
from app.repos.user_repo import UserRepository
from app.utils.parsers.file_manager import FileManager


@dataclass
class FileService:
    file_manager: FileManager = field(default_factory=FileManager)
    import_repo: ImportJobRepository = ImportJobRepository()
    todo_repo: ToDoRepository = ToDoRepository()
    user_repo: UserRepository = UserRepository()

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

    @staticmethod
    def _process_rows_by_user_existence(parsed_rows: list[ParsedRow], existing_ids: set[int]) -> list[ParsedRow]:
        for row in parsed_rows:
            cur_user_id = row.data.get("user_id")

            if cur_user_id and cur_user_id not in existing_ids:
                row.is_valid = False
                row.error = f"User {cur_user_id} not found"

        return parsed_rows

    async def _process_import_job(
        self,
        job_id: int,
        filename: str,
        file_content: bytes,
    ):
        async with session_maker() as session:
            await self.update_import_job(session, job_id, {
                "status": JobStatus.RUNNING,
                "started_at": dt.datetime.now(dt.UTC)
            })

            try:
                parsed_rows = self.file_manager.parse_file(filename, file_content)
                user_ids = [row.data["user_id"] for row in parsed_rows if row.data.get("user_id") is not None]
                existing_ids = await self.user_repo.filter_ids_by_existence(session, user_ids)
                parsed_rows = self._process_rows_by_user_existence(parsed_rows, existing_ids)

                errors = []
                created_count = 0

                for parsed_row in parsed_rows:
                    if parsed_row.is_valid:
                        created_count += 1
                        parsed_row.data.pop("attachments_meta")
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
                    "finished_at": dt.datetime.now(dt.UTC),
                })

            except Exception as e:
                await session.rollback()
                await self.update_import_job(session, job_id, {
                    "status": JobStatus.FAILED,
                    "errors": [{"error": f"Critical: {str(e)}"}],
                    "finished_at": dt.datetime.now(dt.UTC),
                })


@lru_cache
def get_file_service() -> FileService:
    return FileService()
