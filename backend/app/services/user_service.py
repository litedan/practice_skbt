"""Сервис работы с пользователями."""

from datetime import date

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import AppError, NotFoundError, UnauthorizedError
from app.core.security import hash_password, verify_password
from app.models.main.department import Department
from app.models.main.position import Position
from app.models.main.user import User
from app.schemas.user import AdminUserUpdate, ChangePasswordRequest, UserProfileUpdate
from app.services.audit_service import AuditService


class UserService:
    def __init__(self, session: AsyncSession, audit_service: AuditService | None = None) -> None:
        self._session = session
        self._audit = audit_service

    async def get_by_id(self, user_id: int) -> User:
        result = await self._session.execute(
            select(User)
            .options(selectinload(User.position), selectinload(User.department))
            .where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if user is None:
            raise NotFoundError("Пользователь не найден")
        return user

    async def list_users(
        self,
        *,
        department_id: int | None = None,
        position_id: int | None = None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[User]:
        query = (
            select(User)
            .options(selectinload(User.position), selectinload(User.department))
            .order_by(User.full_name.asc())
        )
        if department_id is not None:
            query = query.where(User.department_id == department_id)
        if position_id is not None:
            query = query.where(User.position_id == position_id)
        if search:
            pattern = f"%{search.strip()}%"
            query = query.where(
                or_(User.full_name.ilike(pattern), User.email.ilike(pattern))
            )
        result = await self._session.execute(query.offset(skip).limit(limit))
        return list(result.scalars())

    async def admin_update_user(
        self,
        *,
        user_id: int,
        payload: AdminUserUpdate,
        actor_id: int,
        ip_address: str | None,
        user_agent: str | None,
    ) -> User:
        user = await self.get_by_id(user_id)
        update_data = payload.model_dump(exclude_unset=True)

        if not update_data:
            return user

        old_data = self._user_snapshot(user)

        if "department_id" in update_data and update_data["department_id"] is not None:
            if await self._session.get(Department, update_data["department_id"]) is None:
                raise NotFoundError("Отдел не найден")

        if "position_id" in update_data and update_data["position_id"] is not None:
            if await self._session.get(Position, update_data["position_id"]) is None:
                raise NotFoundError("Должность не найдена")

        if "is_blocked" in update_data:
            if update_data["is_blocked"]:
                user.blocked_at = date.today()
                user.block_reason = update_data.get("block_reason") or user.block_reason
            else:
                user.blocked_at = None
                user.block_reason = None
            update_data.pop("is_blocked", None)
            update_data.pop("block_reason", None)

        for field, value in update_data.items():
            setattr(user, field, value)

        await self._session.flush()

        if self._audit is not None:
            await self._audit.log_entity_change(
                entity_name="users",
                entity_id=user.id,
                action="admin_update",
                user_id=actor_id,
                old_data=old_data,
                new_data=self._user_snapshot(user),
                ip_address=ip_address,
                user_agent=user_agent,
            )

        return await self.get_by_id(user.id)

    async def update_profile(
        self,
        *,
        current_user: User,
        payload: UserProfileUpdate,
        ip_address: str | None,
        user_agent: str | None,
    ) -> User:
        update_data = payload.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_by_id(current_user.id)

        old_data = {
            field: (value.isoformat() if hasattr(value, "isoformat") else value)
            for field, value in ((f, getattr(current_user, f)) for f in update_data)
        }
        for field, value in update_data.items():
            setattr(current_user, field, value)

        await self._session.flush()

        if self._audit is not None:
            new_data = {
                field: (value.isoformat() if hasattr(value, "isoformat") else value)
                for field, value in update_data.items()
            }
            await self._audit.log_entity_change(
                entity_name="users",
                entity_id=current_user.id,
                action="update_profile",
                user_id=current_user.id,
                old_data=old_data,
                new_data=new_data,
                ip_address=ip_address,
                user_agent=user_agent,
            )

        return await self.get_by_id(current_user.id)

    async def change_password(
        self,
        *,
        current_user: User,
        payload: ChangePasswordRequest,
        ip_address: str | None,
        user_agent: str | None,
    ) -> None:
        if not verify_password(payload.current_password, current_user.password_hash):
            raise UnauthorizedError("Неверный текущий пароль")

        if payload.current_password == payload.new_password:
            raise AppError("Новый пароль должен отличаться от текущего")

        current_user.password_hash = hash_password(payload.new_password)
        await self._session.flush()

        if self._audit is not None:
            await self._audit.log_auth_attempt(
                email=current_user.email or str(current_user.id),
                action="password_changed",
                ip_address=ip_address,
                user_agent=user_agent,
            )

    @staticmethod
    def _user_snapshot(user: User) -> dict:
        return {
            "department_id": user.department_id,
            "position_id": user.position_id,
            "blocked_at": user.blocked_at.isoformat() if user.blocked_at else None,
            "block_reason": user.block_reason,
        }
