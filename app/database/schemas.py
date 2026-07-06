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
    user_id: int | None
