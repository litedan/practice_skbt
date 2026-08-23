"""Схемы уведомлений."""

from datetime import datetime

from app.schemas.common import ORMModel


class NotificationRead(ORMModel):
    id: int
    title: str
    message: str
    is_read: bool
    created_at: datetime
    user_id: int
    request_id: int | None
