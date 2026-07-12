from typing import Any

from app.database.schemas import ToDoOutput


def get_ordering_fields(scheme: Any):
    return scheme.model_json_schema()['properties'].keys()


if __name__ == '__main__':
    get_ordering_fields(ToDoOutput)