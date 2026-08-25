from dataclasses import dataclass

from app.database.schemas import ParsedRow
from app.errors.exceptions import FileFormatException
from app.utils.parsers.base_file_handler import BaseFileHandler
from app.utils.parsers.csv_file_handler import CSVFileHandler


@dataclass
class FileManager:
    _handlers: list[BaseFileHandler] = (
        CSVFileHandler(),
    )

    def __post_init__(self):
        self._formats_map = {
            handler.get_format_name(): handler
            for handler in self._handlers
        }

    def get_handler_by_format(self, format_name: str) -> BaseFileHandler:
        handler = self._formats_map.get(format_name)
        if handler is None:
            raise FileFormatException(f"Unknown format: {format_name}")
        return handler

    def get_handler_by_extension(self, file_name: str) -> BaseFileHandler:
        extension = file_name.split(".")[-1]

        for handler in self._handlers:
            if extension in handler.get_extensions():
                return handler

        raise FileFormatException(f"Unknown extension: {extension}")

    def parse_file(self, file_name: str, file_content: bytes) -> list[ParsedRow]:
        handler = self.get_handler_by_extension(file_name)
        return handler.parse_file(file_content)

    def export_file(self, file_format: str, data: list[dict]) -> bytes:
        handler = self.get_handler_by_format(file_format)
        return handler.export_file(data)
