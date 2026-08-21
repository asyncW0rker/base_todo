from abc import ABC, abstractmethod

from app.database.schemas import ParsedRow


class BaseFileHandler(ABC):
    @abstractmethod
    async def parse_file(self, file_content: bytes) -> list[ParsedRow]:
        pass

    @abstractmethod
    async def export_file(self, data: list[dict]) -> bytes:
        pass
