"""Сервис in-app уведомлений."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.main.notification import Notification
from app.models.main.user import User
from app.schemas.notification import NotificationRead


class NotificationService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        user_id: int,
        title: str,
        message: str,
        request_id: int | None = None,
    ) -> Notification:
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            request_id=request_id,
        )
        self._session.add(notification)
        await self._session.flush()
        return notification

    async def list_for_user(self, user: User) -> list[NotificationRead]:
        result = await self._session.execute(
            select(Notification)
            .where(Notification.user_id == user.id)
            .order_by(Notification.created_at.desc())
        )
        return [NotificationRead.model_validate(n) for n in result.scalars()]

    async def mark_read(self, *, user: User, notification_id: int) -> None:
        notification = await self._session.get(Notification, notification_id)
        if notification is None:
            raise NotFoundError("Уведомление не найдено")
        if notification.user_id != user.id:
            raise ForbiddenError("Нет доступа к этому уведомлению")

        notification.is_read = True
        await self._session.flush()

    async def notify_hr_users(
        self,
        *,
        hr_user_ids: list[int],
        title: str,
        message: str,
        request_id: int,
    ) -> None:
        for user_id in hr_user_ids:
            await self.create(
                user_id=user_id,
                title=title,
                message=message,
                request_id=request_id,
            )
