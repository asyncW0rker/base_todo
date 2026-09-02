import datetime as dt
from typing import Any

import pytz
from pydantic import BaseModel, Field, computed_field, field_validator

from app.errors.http_exceptions import HTTPValueError
from app.utils.enum_fabric import generate_ordering_enum, generate_enum_from_fields


possible_roles = ["user", "manager", "admin"]
possible_query_languages = ["russian", "english"]
possible_job_statuses = ["pending", "running", "done", "failed"]
possible_content_types = ["image/jpeg", "image/png", "application/pdf"]

UserRole = generate_enum_from_fields("UserRole", possible_roles)
AnalyticsTimezone = generate_enum_from_fields("AnalyticsTimezone", pytz.all_timezones)
QueryLanguage = generate_enum_from_fields("QueryLanguage", possible_query_languages)
JobStatus = generate_enum_from_fields("JobStatus", possible_job_statuses)
AttachmentContentType = generate_enum_from_fields("AttachmentContentType", possible_content_types)


class HTTPErrorDetail(BaseModel):
    detail: str


class Message(BaseModel):
    message: str


class BaseOrderingParams(BaseModel):
    limit: int = Field(10, gt=0, le=10000)
    offset: int = Field(0, ge=0)


class BaseFilterParams(BaseModel):
    pass


class BaseSearchParams(BaseModel):
    q: str | None = None
    language: QueryLanguage = QueryLanguage.RUSSIAN


class BaseDownloadURL(BaseModel):
    storage_key: str
    download_url: str


class BaseJobOutput(BaseModel):
    id: int
    user_id: int | None = None
    status: JobStatus
    created_at: dt.datetime
    started_at: dt.datetime | None
    finished_at: dt.datetime | None

    class Config:
        from_attributes = True


class AttachmentUploadRequest(BaseModel):
    filename: str
    size: int
    content_type: AttachmentContentType


class AttachmentOutput(BaseModel):
    id: int
    todo_id: int
    storage_key: str | None
    filename: str
    size: int
    content_type: AttachmentContentType
    is_uploaded: bool
    created_at: dt.datetime

    class Config:
        from_attributes = True


class AttachmentUploadURL(BaseModel):
    storage_key: str
    upload_url: str


class AttachmentDownloadURL(BaseDownloadURL):
    pass


class ToDoBase(BaseModel):
    title: str
    description: str | None = None
    user_id: int | None = None


class ToDoCreate(ToDoBase):
    attachments_meta: list[AttachmentUploadRequest] = Field(default_factory=list)


class ToDoUpdate(ToDoBase):
    completed: bool
    version: int

    @computed_field
    def completed_at(self) -> dt.datetime | None:
        return dt.datetime.now(dt.UTC) if self.completed else None


class ToDoPatch(BaseModel):
    title: str | None = None
    description: str | None = None
    user_id: int | None = None
    completed: bool | None = None
    version: int

    @computed_field
    def completed_at(self) -> dt.datetime | None:
        return dt.datetime.now(dt.UTC) if self.completed else None

    def model_dump(self, **kwargs) -> dict:
        return {k: v for k, v in super().model_dump(**kwargs).items() if v is not None}


class ToDoStatusUpdate(BaseModel):
    ids: str
    completed: bool = True

    @computed_field
    def completed_at(self) -> dt.datetime | None:
        return dt.datetime.now(dt.UTC) if self.completed else None

    @field_validator("ids")
    @classmethod
    def process_ids(cls, val):
        try:
            return list(map(int, val.split(",")))
        except (ValueError, TypeError):
            raise HTTPValueError


class ToDoOutput(BaseModel):
    id: int
    title: str
    description: str | None
    completed: bool
    completed_at: dt.datetime | None
    created_at: dt.datetime
    updated_at: dt.datetime
    version: int
    user_id: int | None

    class Config:
        from_attributes = True


class ToDoWithUploads(BaseModel):
    todo: ToDoOutput
    upload_urls: list[AttachmentUploadURL]


ToDoSortingFields = generate_ordering_enum("ToDoSortingFields", ToDoOutput, ["created",])


class ToDoOrderingParams(BaseOrderingParams):
    limit: int = Field(10, gt=0, le=100)
    sort_by: ToDoSortingFields = ToDoSortingFields.CREATED_AT


class ToDoFilterParams(BaseFilterParams):
    completed: bool | None = None
    title_contains: str | None = None
    created_after: dt.date | None = None
    created_before: dt.date | None = None


class ToDoSearchParams(BaseSearchParams):
    pass


class ToDoAnalyticsFilterParams(BaseFilterParams):
    user_id: int | None = None
    timezone: AnalyticsTimezone = AnalyticsTimezone.EUROPE_MOSCOW


class CompletedStats(BaseModel):
    true: int = 0
    false: int = 0


class WeekdayDistribution(BaseModel):
    Monday: int = 0
    Tuesday: int = 0
    Wednesday: int = 0
    Thursday: int = 0
    Friday: int = 0
    Saturday: int = 0
    Sunday: int = 0


class TopWordsAnalyticsItem(BaseModel):
    word: str
    count: int


class ToDoAnalyticsOutput(BaseModel):
    total_count: int
    completed_stats: CompletedStats
    avg_completion_time_hours: float
    weekday_distribution: WeekdayDistribution
    top_words_in_titles: dict[str, int]

    class Config:
        from_attributes = True


class AnalyticsJobOutput(BaseJobOutput):
    params: dict[str, Any]
    result: ToDoAnalyticsOutput | dict


class JobAccepted(BaseModel):
    job_id: int
    status: JobStatus = JobStatus.PENDING


class ParsedRow(BaseModel):
    row_number: int
    data: dict[str, Any]
    is_valid: bool = True
    error: str | None = None


class ImportJobOutput(BaseJobOutput):
    filename: str | None
    created_count: int  | None
    errors: list[dict]


class ExportJobOutput(BaseJobOutput):
    filename: str | None
    format: str | None
    file_path: str | None
    records_count: int | None
    error: str | None


class ExportDownloadUrl(BaseDownloadURL):
    pass


class ToDoExportOrderingParams(BaseOrderingParams):
    pass


class UserBase(BaseModel):
    username: str
    password: str


class UserWithRole(UserBase):
    role: UserRole


class UserCreate(UserWithRole):
    pass


class UserUpdate(UserWithRole):
    pass


class UserOutput(BaseModel):
    id: int
    username: str
    role: UserRole


class UserWithTodos(UserOutput):
    todos: list[ToDoOutput] = Field(default_factory=list)


class AuthData(UserBase):
    pass


class RefreshToken(BaseModel):
    token: str


class AuthOutput(BaseModel):
    access_token: str
    refresh_token: str
