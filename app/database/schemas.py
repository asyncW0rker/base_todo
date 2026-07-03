from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str


class UserOutput(BaseModel):
    id: int
    username: str


class ToDoBase(BaseModel):
    title: str
    description: str


class ToDoCreate(ToDoBase):
    pass


class ToDoUpdate(ToDoBase):
    completed: bool


class ToDoOutput(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
