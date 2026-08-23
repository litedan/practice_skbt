"""Константы и правила переходов статусов заявок."""

from enum import StrEnum


class RequestStatusName(StrEnum):
    NEW = "Новая"
    IN_PROGRESS = "В работе"
    APPROVED = "Одобрена"
    REJECTED = "Отклонена"


# Допустимые переходы: текущий статус -> множество целевых
ALLOWED_STATUS_TRANSITIONS: dict[RequestStatusName, frozenset[RequestStatusName]] = {
    RequestStatusName.NEW: frozenset({RequestStatusName.IN_PROGRESS, RequestStatusName.REJECTED}),
    RequestStatusName.IN_PROGRESS: frozenset(
        {RequestStatusName.APPROVED, RequestStatusName.REJECTED, RequestStatusName.NEW}
    ),
    RequestStatusName.APPROVED: frozenset(),
    RequestStatusName.REJECTED: frozenset({RequestStatusName.NEW}),
}

ALLOWED_UPLOAD_EXTENSIONS = frozenset({".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx"})
MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
