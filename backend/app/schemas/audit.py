"""Схемы аудита (LogBD)."""

from datetime import datetime

from app.schemas.common import ORMModel


class AuditLogRead(ORMModel):
    id: int
    entity_name: str
    entity_id: int
    action: str
    old_data: dict | None = None
    new_data: dict | None = None
    user_id: int | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    created_at: datetime
