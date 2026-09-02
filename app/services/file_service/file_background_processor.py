import datetime as dt
from dataclasses import dataclass
from functools import lru_cache

from app.database.db import session_maker
from app.database.schemas import JobStatus, ToDoOutput
from app.services.file_service.file_service_base import FileServiceBase


@dataclass
class FileBackgroundProcessor(FileServiceBase):
    async def process_import_job(
        self,
        job_id: int,
        filename: str,
        file_content: bytes,
    ) -> None:
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

    async def process_export_job(self, job_id: int, data: list[dict]) -> None:
        async with session_maker() as session:
            try:
                job = await self.update_export_job(session, job_id, {
                    "status": JobStatus.RUNNING,
                    "started_at": dt.datetime.now(dt.UTC)
                })
                file_bytes, content_type = self.file_manager.export_data(job.format, data)

                timestamp = dt.datetime.now(dt.UTC).strftime("%Y-%m-%d %H:%M:%S")
                filename = f"export_{job.id}_{timestamp}.{job.format}"
                storage_key = self.s3_manager.generate_file_key_for_exports(job.user_id, filename)

                await self.s3_manager.upload_bytes(storage_key, file_bytes, content_type)

                await self.update_export_job(session, job_id, {
                    "status": JobStatus.DONE,
                    "finished_at": dt.datetime.now(dt.UTC),
                    "filename": filename,
                    "file_path": storage_key,
                })

            except Exception as e:
                await session.rollback()
                await self.update_export_job(session, job_id, {
                    "status": JobStatus.FAILED,
                    "error": f"Critical: {str(e)}",
                    "finished_at": dt.datetime.now(dt.UTC),
                })


@lru_cache
def get_file_processor():
    return FileBackgroundProcessor()
