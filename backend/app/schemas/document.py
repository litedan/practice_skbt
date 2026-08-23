"""Схемы документов (подписание — заглушка)."""

from datetime import datetime

from app.schemas.common import ORMModel


class DocumentSignResponse(ORMModel):
    document_id: int
    status: str
    message: str
    signed_at: datetime | None = None
