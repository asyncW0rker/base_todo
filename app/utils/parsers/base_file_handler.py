from abc import ABC, abstractmethod

from app.database.schemas import ParsedRow


class BaseFileHandler(ABC):
    @abstractmethod
    def parse_file(self, file_content: bytes) -> list[ParsedRow]:
        pass

    @abstractmethod
    def export_file(self, data: list[dict]) -> bytes:
        pass

    @staticmethod
    @abstractmethod
    def get_extensions() -> list[str]:
        pass

    @staticmethod
    @abstractmethod
    def get_format_name() -> str:
        pass

    @staticmethod
    @abstractmethod
    def get_content_type() -> str:
        pass
