from datetime import datetime, date

import pytz
from pydantic import BaseModel, Field, computed_field

from app.utils.enum_fabric import generate_ordering_enum, generate_enum_from_fields


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


class BaseOrderingParams(BaseModel):
    limit: int = Field(10, gt=0, le=100)
    offset: int = Field(0, ge=0)


class BaseFilterParams(BaseModel):
    pass


ToDoSortingFields = generate_ordering_enum("ToDoSortingFields", ToDoOutput, ["created",])
AvailableTimezones = generate_enum_from_fields("AvailableTimezones", pytz.all_timezones)


class ToDoOrderingParams(BaseOrderingParams):
    sort_by: ToDoSortingFields = ToDoSortingFields.CREATED_AT


class ToDoFilterParams(BaseFilterParams):
    completed: bool | None = None
    title_contains: str | None = None
    created_after: date | None = None
    created_before: date | None = None


class ToDoAnalyticsFilterParams(BaseFilterParams):
    timezone: AvailableTimezones = AvailableTimezones.EUROPE_MOSCOW


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


class ToDoAnalyticsOutput(BaseModel):
    total_count: int
    completed_stats: CompletedStats
    avg_completion_time_hours: float
    weekday_distribution: WeekdayDistribution

    class Config:
        from_attributes = True


class ToDoStatusUpdate(BaseModel):
    ids: list[int]
    completed: bool = True

    @computed_field
    def completed_at(self):
        return datetime.now() if self.completed else None
