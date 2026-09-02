from typing import Any, Sequence

from app.services.file_service.file_background_processor import get_file_processor, FileBackgroundProcessor
from app.utils.background.broker import broker


@broker.task("process_import_job")
async def process_import_job(job_id: int, filename: str, file_content: bytes) -> None:
    file_processor: FileBackgroundProcessor = get_file_processor()
    return await file_processor.process_import_job(job_id, filename, file_content)


@broker.task("process_export_job")
async def process_export_job(job_id: int, data: Sequence[Any]) -> None:
    file_processor: FileBackgroundProcessor = get_file_processor()
    return await file_processor.process_export_job(job_id, data)
