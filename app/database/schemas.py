from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    password: str


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    pass


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
