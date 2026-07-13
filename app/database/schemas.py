from datetime import datetime, UTC

from pydantic import BaseModel, Field, computed_field

from app.utils.ordering_enum_fabric import generate_ordering_enum


class UserBase(BaseModel):
    username: str
    password: str


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    pass


class ToDoBase(BaseModel):
    title: str
    description: str
    user_id: int | None = None


class ToDoCreate(ToDoBase):
    pass


class ToDoUpdate(ToDoBase):
    completed: bool

    @computed_field
    def completed_at(self) -> datetime | None:
        return datetime.now() if self.completed else None


class ToDoOutput(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    completed_at: datetime | None
    created_at: datetime
    user_id: int | None


class UserOutput(BaseModel):
    id: int
    username: str
    todos: list[ToDoOutput]


class BaseFilterParams(BaseModel):
    limit: int = Field(10, gt=0, le=100)
    offset: int = Field(0, ge=0)


ToDoSortingFields = generate_ordering_enum("ToDoSortingFields", ToDoOutput)


class ToDoFilterParams(BaseFilterParams):
    sort_by: ToDoSortingFields = ToDoSortingFields.CREATED_AT
