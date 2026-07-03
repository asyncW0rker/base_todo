from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    password: Mapped[str]

    todos: Mapped[list["ToDo"]] = relationship(back_populates="user")


class ToDo(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    description: Mapped[str]
    completed: Mapped[bool] = mapped_column(default=False)

    user_id: Mapped[int | None] = mapped_column(ForeignKey(User.id, ondelete="CASCADE"), nullable=True)
    user: Mapped[User] = relationship(back_populates="todos")
