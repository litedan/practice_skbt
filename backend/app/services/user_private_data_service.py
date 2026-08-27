"""
Сервис персональных данных (ПД).

Доступ HR/руководителя к чужим ПД логируется в sensitive_access_log.
Просмотр/правка своего профиля не пишется в этот лог.
"""

from sqlalchemy import and_, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.core.rbac import can_read_private_data, can_update_private_data
from app.models.main.user import User
from app.models.main.user_private_data import UserPrivateData
from app.schemas.user_private_data import UserPrivateDataRead, UserPrivateDataUpdate
from app.services.audit_service import AuditService

_UNIQUE_FIELDS: tuple[tuple[str, str], ...] = (
    ("passport", "Паспорт"),
    ("snils", "СНИЛС"),
    ("inn", "ИНН"),
    ("military_id", "Военный билет"),
)


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

        if current_user.id != target_user_id:
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

        await self._ensure_unique_documents(
            owner_user_id=target_user_id,
            values=update_data,
        )

        for field, value in update_data.items():
            setattr(private_data, field, value)

        try:
            await self._session.flush()
        except IntegrityError as exc:
            raise ConflictError(
                "Документ или реквизит уже используется другим сотрудником"
            ) from exc

        await self._session.refresh(private_data)

        if current_user.id != target_user_id:
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

    async def _ensure_unique_documents(
        self,
        *,
        owner_user_id: int,
        values: dict,
    ) -> None:
        for field, label in _UNIQUE_FIELDS:
            if field not in values:
                continue
            value = values[field]
            if value is None:
                continue
            column = getattr(UserPrivateData, field)
            result = await self._session.execute(
                select(UserPrivateData.user_id).where(
                    and_(
                        func.lower(func.trim(column)) == str(value).strip().lower(),
                        UserPrivateData.user_id != owner_user_id,
                    )
                )
            )
            if result.scalar_one_or_none() is not None:
                raise ConflictError(f"{label} уже используется другим сотрудником")

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
