"""Сервис авторизации."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import UnauthorizedError
from app.core.permissions import RoleCode
from app.core.security import (
    TOKEN_TYPE_ACCESS,
    TOKEN_TYPE_REFRESH,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.models.main.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.audit_service import AuditService


class AuthService:
    def __init__(self, main_session: AsyncSession, audit_service: AuditService) -> None:
        self._main_session = main_session
        self._audit = audit_service

    async def login(
        self,
        payload: LoginRequest,
        *,
        ip_address: str | None,
        user_agent: str | None,
    ) -> TokenResponse:
        user = await self._get_user_by_email(payload.email)

        if user is None or not verify_password(payload.password, user.password):
            await self._audit.log_auth_attempt(
                email=payload.email,
                action="login_failed",
                ip_address=ip_address,
                user_agent=user_agent,
                fail_reason="invalid_credentials",
            )
            raise UnauthorizedError("Неверный email или пароль")

        if user.is_blocked:
            await self._audit.log_auth_attempt(
                email=payload.email,
                action="login_failed",
                ip_address=ip_address,
                user_agent=user_agent,
                fail_reason="user_blocked",
            )
            raise UnauthorizedError("Учётная запись заблокирована")

        await self._audit.log_auth_attempt(
            email=payload.email,
            action="login_success",
            ip_address=ip_address,
            user_agent=user_agent,
        )

        subject = str(user.id)
        role_code = user.role.code if user.role else RoleCode.EMPLOYEE
        return TokenResponse(
            access_token=create_access_token(subject, extra_claims={"role": role_code}),
            refresh_token=create_refresh_token(subject),
        )

    async def refresh(self, refresh_token: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)
        except Exception as exc:
            raise UnauthorizedError("Невалидный refresh-токен") from exc

        if payload.get("type") != TOKEN_TYPE_REFRESH:
            raise UnauthorizedError("Ожидается refresh-токен")

        subject = payload.get("sub")
        if not subject:
            raise UnauthorizedError("Невалидный refresh-токен")

        user = await self._get_user_by_id(int(subject))
        if user is None or user.is_blocked:
            raise UnauthorizedError("Пользователь не найден или заблокирован")

        role_code = user.role.code if user.role else RoleCode.EMPLOYEE
        return TokenResponse(
            access_token=create_access_token(subject, extra_claims={"role": role_code}),
            refresh_token=create_refresh_token(subject),
        )

    async def get_user_from_access_token(self, token: str) -> User:
        try:
            payload = decode_token(token)
        except Exception as exc:
            raise UnauthorizedError("Невалидный access-токен") from exc

        if payload.get("type") != TOKEN_TYPE_ACCESS:
            raise UnauthorizedError("Ожидается access-токен")

        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedError("Невалидный access-токен")

        user = await self._get_user_by_id(int(user_id))
        if user is None or user.is_blocked:
            raise UnauthorizedError("Пользователь не найден или заблокирован")

        return user

    async def _get_user_by_email(self, email: str) -> User | None:
        result = await self._main_session.execute(
            select(User).options(selectinload(User.role)).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def _get_user_by_id(self, user_id: int) -> User | None:
        result = await self._main_session.execute(
            select(User).options(selectinload(User.role)).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
