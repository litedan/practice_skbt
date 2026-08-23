"""Схемы кадровых заявок."""

from datetime import date, datetime

from pydantic import Field, model_validator

from app.schemas.common import ORMModel


def _validate_date_range(date_from: date | None, date_to: date | None) -> None:
    if (date_from is None) ^ (date_to is None):
        raise ValueError("date_from и date_to должны быть указаны вместе")
    if date_from is not None and date_to is not None and date_from > date_to:
        raise ValueError("date_from не может быть позже date_to")


class StatusBrief(ORMModel):
    id: int
    name: str


class RequestTypeBrief(ORMModel):
    id: int
    name: str


class UserBrief(ORMModel):
    id: int
    full_name: str
    email: str


class RequestCreate(ORMModel):
    request_type_id: int
    comment: str | None = Field(default=None, max_length=5000)
    date_from: date | None = None
    date_to: date | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> "RequestCreate":
        _validate_date_range(self.date_from, self.date_to)
        return self


class RequestUpdate(ORMModel):
    """PATCH — HR меняет статус/checker; сотрудник может обновить comment/dates своей «Новой» заявки."""

    status_id: int | None = None
    comment: str | None = Field(default=None, max_length=5000)
    checker_id: int | None = None
    date_from: date | None = None
    date_to: date | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> "RequestUpdate":
        if self.date_from is not None and self.date_to is not None and self.date_from > self.date_to:
            raise ValueError("date_from не может быть позже date_to")
        return self


class DocumentFileRead(ORMModel):
    id: int
    name: str
    request_id: int


class RequestRead(ORMModel):
    id: int
    comment: str | None
    date_from: date | None
    date_to: date | None
    creator_id: int
    checker_id: int | None
    status_id: int
    request_type_id: int
    created_at: datetime
    updated_at: datetime
    status: StatusBrief
    request_type: RequestTypeBrief
    creator: UserBrief | None = None
    checker: UserBrief | None = None


class RequestDetailRead(RequestRead):
    document_files: list[DocumentFileRead] = []


class RequestStatsRead(ORMModel):
    total: int
    new: int
    in_progress: int
    approved: int
    rejected: int
