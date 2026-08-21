import csv
import io
from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from app.database.schemas import ParsedRow, ToDoCreate
from app.utils.parsers.base_file_handler import BaseFileHandler


@dataclass
class CSVFileHandler(BaseFileHandler):
    data_model: Any = ToDoCreate

    def parse_file(self, file_content: bytes) -> list[ParsedRow]:
        result = []

        try:
            text = file_content.decode("utf-8")
            reader = csv.DictReader(io.StringIO(text))

            for row_num, row in enumerate(reader, start=1):
                try:
                    parsed_data = self.data_model(**row)
                    result.append(ParsedRow(
                        row_number=row_num,
                        data=parsed_data.model_dump(),
                        is_valid=True,
                    ))
                except ValidationError as e:
                    result.append(ParsedRow(
                        row_number=row_num,
                        data=row,
                        is_valid=False,
                        error=str(e),
                    ))
        except Exception as e:
            result.append(ParsedRow(
                row_number=0,
                data={},
                is_valid=False,
                error=f"Parsing failed: {str(e)}",
            ))

        return result

    def export_file(self, data: list[dict]) -> bytes:
        if not data:
            return b""

        output = io.StringIO()
        field_names = list(data[0].keys())

        writer = csv.DictWriter(output, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(data)

        return output.getvalue().encode("utf-8")

    @staticmethod
    def get_extensions() -> list[str]:
        return [".csv"]

    @staticmethod
    def get_format_name() -> str:
        return "csv"
