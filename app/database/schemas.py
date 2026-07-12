from datetime import datetime

from pydantic import BaseModel, Field


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


class ToDoFilterParams(BaseFilterParams):
    pass
