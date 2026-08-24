"""Схемы кадровых заявок."""

from datetime import datetime

from pydantic import Field

from app.schemas.common import ORMModel


class StatusBrief(ORMModel):
    id: int
    name: str


class RequestTypeBrief(ORMModel):
    id: int
    name: str
    file_path: str | None = None


class UserBrief(ORMModel):
    id: int
    full_name: str
    email: str | None = None


class RequestCreate(ORMModel):
    request_type_id: int
    comment: str | None = Field(default=None, max_length=5000)


class RequestUpdate(ORMModel):
    status_id: int | None = None
    comment: str | None = Field(default=None, max_length=5000)
    reviewer_id: int | None = None
    approver_id: int | None = None


class DocumentFileRead(ORMModel):
    id: int
    name: str
    request_id: int


class RequestRead(ORMModel):
    id: int
    comment: str | None
    employee_id: int
    reviewer_id: int | None
    approver_id: int | None
    status_id: int
    request_type_id: int
    created_at: datetime
    updated_at: datetime
    status: StatusBrief
    request_type: RequestTypeBrief
    employee: UserBrief | None = None
    reviewer: UserBrief | None = None
    approver: UserBrief | None = None


class RequestDetailRead(RequestRead):
    document_files: list[DocumentFileRead] = []


class RequestStatsRead(ORMModel):
    total: int
    created: int
    in_review: int
    in_approval: int
    approved: int
    rejected: int
    closed: int
