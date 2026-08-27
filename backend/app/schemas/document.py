"""Схемы документов."""

from datetime import datetime

from pydantic import Field

from app.schemas.common import ORMModel


class DocumentSignRequest(ORMModel):
    password: str = Field(min_length=8, max_length=128)


class DocumentSignResponse(ORMModel):
    document_id: int
    status: str
    message: str
    signed_at: datetime | None = None
