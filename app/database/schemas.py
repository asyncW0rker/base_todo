import datetime as dt

import pytz
from pydantic import BaseModel, Field, computed_field, field_validator

from app.errors.exceptions import HTTPValueError
from app.utils.enum_fabric import generate_ordering_enum, generate_enum_from_fields


possible_roles = ["user", "manager", "admin"]
possible_query_languages = ["russian", "english"]
possible_job_statuses = ["pending", "running", "done", "failed"]

UserRole = generate_enum_from_fields("UserRole", possible_roles)
AnalyticsTimezone = generate_enum_from_fields("AnalyticsTimezone", pytz.all_timezones)
QueryLanguage = generate_enum_from_fields("QueryLanguage", possible_query_languages)
AnalyticsJobStatus = generate_enum_from_fields("AnalyticsJobStatus", possible_job_statuses)


class BaseOrderingParams(BaseModel):
    limit: int = Field(10, gt=0, le=100)
    offset: int = Field(0, ge=0)


class BaseFilterParams(BaseModel):
    pass


class BaseSearchParams(BaseModel):
    q: str | None = None
    language: QueryLanguage = QueryLanguage.RUSSIAN


class ToDoBase(BaseModel):
    title: str
    description: str
    user_id: int | None = None


class ToDoCreate(ToDoBase):
    pass


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


class ToDoOutput(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    completed_at: dt.datetime | None
    created_at: dt.datetime
    updated_at: dt.datetime
    version: int
    user_id: int | None

    class Config:
        from_attributes = True


ToDoSortingFields = generate_ordering_enum("ToDoSortingFields", ToDoOutput, ["created",])


class ToDoOrderingParams(BaseOrderingParams):
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


class UserBase(BaseModel):
    username: str
    password: str


class UserWithRole(UserBase):
    role: UserRole = UserRole.USER


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
