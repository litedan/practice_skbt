"""
Сервис персональных данных (ПД).

Каждый доступ к ПД логируется в sensitive_acces_log.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, NotFoundError
from app.core.rbac import can_read_private_data, can_update_private_data
from app.models.main.user import User
from app.models.main.user_private_data import UserPrivateData
from app.schemas.user_private_data import UserPrivateDataRead, UserPrivateDataUpdate
from app.services.audit_service import AuditService


class UserPrivateDataService:
    def __init__(self, session: AsyncSession, audit_service: AuditService) -> None:
        self._session = session
        self._audit = audit_service

    async def get_private_data(
        self,
        *,
        target_user_id: int,
        current_user: User,
        ip_address: str | None,
        user_agent: str | None,
    ) -> UserPrivateDataRead:
        self._ensure_read_access(current_user, target_user_id)

        private_data = await self._get_or_create(target_user_id)

        await self._audit.log_sensitive_access(
            user_id=current_user.id,
            target_user_id=target_user_id,
            data_type="user_private_data",
            action="read",
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return UserPrivateDataRead.model_validate(private_data)

    async def update_private_data(
        self,
        *,
        target_user_id: int,
        current_user: User,
        payload: UserPrivateDataUpdate,
        ip_address: str | None,
        user_agent: str | None,
    ) -> UserPrivateDataRead:
        self._ensure_update_access(current_user, target_user_id)

        private_data = await self._get_or_create(target_user_id)
        update_data = payload.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(private_data, field, value)

        await self._session.flush()
        await self._session.refresh(private_data)

        await self._audit.log_sensitive_access(
            user_id=current_user.id,
            target_user_id=target_user_id,
            data_type="user_private_data",
            action="update",
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return UserPrivateDataRead.model_validate(private_data)

    def _ensure_read_access(self, current_user: User, target_user_id: int) -> None:
        if not can_read_private_data(current_user, target_user_id):
            raise ForbiddenError("Нет прав на просмотр персональных данных")

    def _ensure_update_access(self, current_user: User, target_user_id: int) -> None:
        if not can_update_private_data(current_user, target_user_id):
            raise ForbiddenError("Нет прав на изменение персональных данных")

    async def _get_or_create(self, user_id: int) -> UserPrivateData:
        user = await self._session.get(User, user_id)
        if user is None:
            raise NotFoundError("Пользователь не найден")

        result = await self._session.execute(
            select(UserPrivateData).where(UserPrivateData.user_id == user_id)
        )
        private_data = result.scalar_one_or_none()

        if private_data is None:
            private_data = UserPrivateData(user_id=user_id)
            self._session.add(private_data)
            await self._session.flush()

        return private_data
