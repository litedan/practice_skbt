"""Константы и правила переходов статусов заявок."""

from enum import StrEnum

from app.core.permissions import Permission, RoleCode


class RequestStatusName(StrEnum):
    CREATED = "Создана"
    IN_REVIEW = "На проверке"
    IN_APPROVAL = "На согласовании"
    APPROVED = "Одобрена"
    REJECTED = "Отклонена"
    CLOSED = "Закрыта"


ALLOWED_STATUS_TRANSITIONS: dict[RequestStatusName, frozenset[RequestStatusName]] = {
    RequestStatusName.CREATED: frozenset({RequestStatusName.IN_REVIEW, RequestStatusName.REJECTED}),
    RequestStatusName.IN_REVIEW: frozenset(
        {RequestStatusName.IN_APPROVAL, RequestStatusName.REJECTED, RequestStatusName.CREATED}
    ),
    RequestStatusName.IN_APPROVAL: frozenset(
        {RequestStatusName.APPROVED, RequestStatusName.REJECTED, RequestStatusName.IN_REVIEW}
    ),
    RequestStatusName.APPROVED: frozenset({RequestStatusName.CLOSED}),
    RequestStatusName.REJECTED: frozenset({RequestStatusName.CREATED}),
    RequestStatusName.CLOSED: frozenset(),
}

STATUS_TRANSITION_ROLES: dict[RequestStatusName, frozenset[RoleCode]] = {
    RequestStatusName.IN_REVIEW: frozenset({RoleCode.HR}),
    RequestStatusName.IN_APPROVAL: frozenset({RoleCode.HR}),
    RequestStatusName.APPROVED: frozenset({RoleCode.MANAGER}),
    RequestStatusName.REJECTED: frozenset({RoleCode.HR, RoleCode.MANAGER}),
    RequestStatusName.CREATED: frozenset({RoleCode.HR}),
    RequestStatusName.CLOSED: frozenset({RoleCode.HR}),
}

STATUS_TRANSITION_PERMISSION: dict[RequestStatusName, Permission] = {
    RequestStatusName.IN_REVIEW: Permission.REQUESTS_REVIEW,
    RequestStatusName.IN_APPROVAL: Permission.REQUESTS_REVIEW,
    RequestStatusName.CREATED: Permission.REQUESTS_REVIEW,
    RequestStatusName.CLOSED: Permission.REQUESTS_REVIEW,
    RequestStatusName.APPROVED: Permission.REQUESTS_APPROVE,
    RequestStatusName.REJECTED: Permission.REQUESTS_REVIEW,
}

ALLOWED_UPLOAD_EXTENSIONS = frozenset({".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx"})
MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024
UPLOADABLE_STATUSES = frozenset({RequestStatusName.CREATED, RequestStatusName.IN_REVIEW})
