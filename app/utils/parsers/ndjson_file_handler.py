import json
from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from app.database.schemas import ToDoCreate, ParsedRow
from app.utils.parsers.base_file_handler import BaseFileHandler


@dataclass
class NDJSONFileHandler(BaseFileHandler):
    data_model: Any = ToDoCreate

    def parse_file(self, file_content: bytes) -> list[ParsedRow]:
        result = []

        try:
            text = file_content.decode("utf-8-sig")

            for row_num, line in enumerate(text.splitlines(), start=1):
                line = line.strip()
                if not line:
                    continue

                try:
                    raw_obj = json.loads(line)

                    if not isinstance(raw_obj, dict):
                        result.append(ParsedRow(
                            row_number=row_num,
                            data={"_raw": raw_obj},
                            is_valid=False,
                            error="Each line must be a JSON object",
                        ))
                        continue

                    parsed_data = self.data_model(**raw_obj)

                    result.append(ParsedRow(
                        row_number=row_num,
                        data=parsed_data.model_dump(),
                        is_valid=True,
                    ))
                except json.JSONDecodeError as e:
                    result.append(ParsedRow(
                        row_number=row_num,
                        data={"_raw": line},
                        is_valid=False,
                        error=f"Invalid JSON: {e}",
                    ))
                except ValidationError as e:
                    result.append(ParsedRow(
                        row_number=row_num,
                        data=raw_obj if isinstance(raw_obj, dict) else {},
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

        lines = [
            json.dumps(row, ensure_ascii=False, default=str)
            for row in data
        ]
        return "\n".join(lines).encode("utf-8")

    @staticmethod
    def get_extensions() -> list[str]:
        return [".ndjson", ".jsonl"]

    @staticmethod
    def get_format_name() -> str:
        return "ndjson"

    @staticmethod
    def get_content_type() -> str:
        return "application/x-ndjson"
