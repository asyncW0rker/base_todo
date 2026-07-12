from enum import StrEnum
from typing import Any


def get_ordering_fields(schema: Any):
    return list(schema.model_json_schema()["properties"].keys())


def create_ordering_values_from_fields(fields: list[str]) -> dict[str, str]:
    enum_vals = {val.upper(): val for val in fields}
    desc_enum_vals = {f"{val.upper()}_DESC": f"-{val}" for val in fields}
    enum_vals.update(desc_enum_vals)
    return enum_vals


def create_ordering_enum_class(class_name: str, enum_vals: dict[str, str]) -> StrEnum:
    return StrEnum(class_name, enum_vals)


def generate_ordering_enum(name: str, schema: Any) -> StrEnum:
    fields = get_ordering_fields(schema)
    enum_vals = create_ordering_values_from_fields(fields)
    return create_ordering_enum_class(name, enum_vals)
