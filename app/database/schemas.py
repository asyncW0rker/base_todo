from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str


class UserOutput(BaseModel):
    id: int
    username: str
