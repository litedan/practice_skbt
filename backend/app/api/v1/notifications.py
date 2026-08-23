"""Уведомления пользователя."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, NotificationServiceDep, require_permission
from app.core.permissions import Permission
from app.models.main.user import User
from app.schemas.common import MessageResponse
from app.schemas.notification import NotificationRead

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=list[NotificationRead])
async def list_notifications(
    current_user: Annotated[User, Depends(require_permission(Permission.NOTIFICATIONS_READ_SELF))],
    service: NotificationServiceDep,
) -> list[NotificationRead]:
    """Список уведомлений текущего пользователя."""
    return await service.list_for_user(current_user)


@router.patch("/{notification_id}/read", response_model=MessageResponse)
async def mark_notification_read(
    notification_id: int,
    current_user: Annotated[
        User, Depends(require_permission(Permission.NOTIFICATIONS_MARK_READ_SELF))
    ],
    service: NotificationServiceDep,
) -> MessageResponse:
    """Пометить уведомление как прочитанное."""
    await service.mark_read(user=current_user, notification_id=notification_id)
    return MessageResponse(detail="Уведомление помечено прочитанным")
