from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import ImportJob, ExportJob
from app.database.schemas import ParsedRow
from app.errors.http_exceptions import HTTPImportJobNotFoundException, HTTPExportJobNotFoundException
from app.repos.export_job_repo import ExportJobRepository
from app.repos.import_job_repo import ImportJobRepository
from app.repos.todo_repo import ToDoRepository
from app.repos.user_repo import UserRepository
from app.utils.parsers.file_manager import FileManager
from app.utils.s3_manager import S3Manager


@dataclass
class FileServiceBase:
    file_manager: FileManager = field(default_factory=FileManager)
    s3_manager: S3Manager = field(default_factory=S3Manager)
    import_repo: ImportJobRepository = ImportJobRepository()
    export_repo: ExportJobRepository = ExportJobRepository()
    todo_repo: ToDoRepository = ToDoRepository()
    user_repo: UserRepository = UserRepository()

    @staticmethod
    def _process_rows_by_user_existence(parsed_rows: list[ParsedRow], existing_ids: set[int]) -> list[ParsedRow]:
        for row in parsed_rows:
            cur_user_id = row.data.get("user_id")

            if cur_user_id and cur_user_id not in existing_ids:
                row.is_valid = False
                row.error = f"User {cur_user_id} not found"

        return parsed_rows

    async def get_import_job(self, session: AsyncSession, job_id: int) -> ImportJob:
        import_job = await self.import_repo.get_one(session, job_id)
        if import_job is None:
            raise HTTPImportJobNotFoundException
        return import_job

    async def get_export_job(self, session: AsyncSession, job_id: int) -> ExportJob:
        export_job = await self.export_repo.get_one(session, job_id)
        if export_job is None:
            raise HTTPExportJobNotFoundException
        return export_job

    async def update_import_job_uncommited(
        self, session: AsyncSession, job_id: int, update_data: dict[str, Any]
    )-> ImportJob:
        job = await self.import_repo.update_one_uncommited(session, job_id, dict(), update_data)
        if job is None:
            raise HTTPImportJobNotFoundException
        return job

    async def update_import_job(self, session: AsyncSession, job_id: int, update_data: dict[str, Any]) -> ImportJob:
        job = await self.update_import_job_uncommited(session, job_id, update_data)
        await session.commit()
        return job

    async def update_export_job(self, session: AsyncSession, job_id: int, update_data: dict[str, Any]) -> ExportJob:
        job = await self.export_repo.update_one(session, job_id, dict(), update_data)
        if job is None:
            raise HTTPExportJobNotFoundException
        return job
