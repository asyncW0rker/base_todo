from enum import StrEnum
from typing import Any


def get_ordering_fields(schema: Any, exclude_fields: list[str] | None = None) -> list[Any]:
    fields = schema.model_json_schema()["properties"].keys()
    if exclude_fields:
        return list(filter(lambda f: f not in exclude_fields, fields))
    return list(fields)


def create_values_from_fields(fields: list[str]) -> dict[str, str]:
    return {
        val.upper().replace("/", "_"): val
        for val in fields
    }


def create_ordering_values_from_fields(fields: list[str]) -> dict[str, str]:
    enum_vals = create_values_from_fields(fields)
    desc_enum_vals = {f"{val.upper()}_DESC": f"-{val}" for val in fields}
    enum_vals.update(desc_enum_vals)
    return enum_vals


def create_ordering_enum_class(class_name: str, enum_vals: dict[str, str]) -> StrEnum:
    return StrEnum(class_name, enum_vals)


def generate_ordering_enum(
    class_name: str,
    schema: Any,
    exclude_fields: list[str] | None = None
) -> StrEnum:
    fields = get_ordering_fields(schema, exclude_fields=exclude_fields)
    enum_vals = create_ordering_values_from_fields(fields)
    return create_ordering_enum_class(class_name, enum_vals)


def generate_enum_from_fields(
    class_name: str,
    fields: list[str],
) -> StrEnum:
    enum_vals = create_values_from_fields(fields)
    return create_ordering_enum_class(class_name, enum_vals)
