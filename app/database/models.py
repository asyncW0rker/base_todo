import datetime as dt
from typing import Any

from sqlalchemy import ForeignKey, Enum, Computed, Index, func, text, String
from sqlalchemy.dialects.postgresql import TIMESTAMP, TSVECTOR, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base
from app.database.schemas import UserRole, AnalyticsJobStatus, AttachmentContentType


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str]
    role: Mapped[str] = mapped_column(Enum(UserRole), default=UserRole.USER)

    todos: Mapped[list["ToDo"]] = relationship(back_populates="user")


class ToDo(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    description: Mapped[str]
    completed: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[dt.datetime] = mapped_column(default=dt.datetime.now)
    updated_at: Mapped[dt.datetime] = mapped_column(default=dt.datetime.now, onupdate=dt.datetime.now)
    completed_at: Mapped[dt.datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    version: Mapped[int] = mapped_column(default=1)

    user_id: Mapped[int | None] = mapped_column(ForeignKey(User.id, ondelete="CASCADE"), nullable=True)
    user: Mapped[User] = relationship(back_populates="todos")

    attachments: Mapped[list["Attachment"]] = relationship(back_populates="todo")

    search_vector: Mapped[TSVECTOR] = mapped_column(
        TSVECTOR,
        Computed(
            "setweight(to_tsvector('russian', coalesce(title, '')), 'A') || "
            "setweight(to_tsvector('russian', coalesce(description, '')), 'B')",
            persisted=True
        ),
        nullable=True,
    )

    __table_args__ = (
        Index("idx_todo_search", search_vector, postgresql_using="gin"),
        Index(
            "idx_todo_title_trgm",
            func.lower(text("title")).label("lower_title"),
            postgresql_using="gin",
            postgresql_ops={"lower_title": "gin_trgm_ops"},
        )
    )


class Token(Base):
    __tablename__ = "tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    refresh_token: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id, ondelete="CASCADE"))
    created_at: Mapped[dt.datetime] = mapped_column(default=dt.datetime.now)
    expires_at: Mapped[dt.datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)


class AnalyticsJob(Base):
    __tablename__ = "analytics_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(Enum(AnalyticsJobStatus), default=AnalyticsJobStatus.PENDING)
    params: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    result: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[dt.datetime] = mapped_column(TIMESTAMP(timezone=True), default=dt.datetime.now)
    started_at: Mapped[dt.datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    finished_at: Mapped[dt.datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)


class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str]
    size: Mapped[int]
    content_type: Mapped[str] = mapped_column(Enum(AttachmentContentType), nullable=False)
    storage_key: Mapped[str]
    created_at: Mapped[dt.datetime] = mapped_column(TIMESTAMP(timezone=True), default=dt.datetime.now)
    is_uploaded: Mapped[bool] = mapped_column(default=False)

    todo_id: Mapped[int] = mapped_column(ForeignKey(ToDo.id, ondelete="CASCADE"), nullable=False)
    todo: Mapped[ToDo] = relationship(back_populates="attachments", lazy="noload")
