"""Сервис авторизации: login / refresh / logout."""

from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import UnauthorizedError
from app.core.rbac import get_user_role_code
from app.core.security import (
    TOKEN_TYPE_ACCESS,
    TOKEN_TYPE_REFRESH,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.models.main.refresh_token import RefreshToken
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

        if user is None or not verify_password(payload.password, user.password_hash):
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
        return await self._issue_tokens(user)

    async def refresh(self, refresh_token: str) -> TokenResponse:
        stored = await self._get_active_refresh(refresh_token)
        user = await self._get_user_by_id(stored.user_id)
        if user is None or user.is_blocked:
            raise UnauthorizedError("Пользователь не найден или заблокирован")

        stored.revoked_at = datetime.now(UTC)
        return await self._issue_tokens(user)

    async def logout(
        self,
        *,
        user: User,
        refresh_token: str | None,
        all_sessions: bool,
        ip_address: str | None,
        user_agent: str | None,
    ) -> None:
        now = datetime.now(UTC)
        if all_sessions:
            await self._main_session.execute(
                update(RefreshToken)
                .where(RefreshToken.user_id == user.id, RefreshToken.revoked_at.is_(None))
                .values(revoked_at=now)
            )
        elif refresh_token:
            stored = await self._get_active_refresh(refresh_token)
            if stored.user_id != user.id:
                raise UnauthorizedError("Refresh-токен принадлежит другому пользователю")
            stored.revoked_at = now
        else:
            raise UnauthorizedError("Передайте refresh_token или all_sessions=true")

        await self._audit.log_auth_attempt(
            email=user.email or "",
            action="logout",
            ip_address=ip_address,
            user_agent=user_agent,
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

    async def _issue_tokens(self, user: User) -> TokenResponse:
        subject = str(user.id)
        role_code = get_user_role_code(user)
        refresh, jti, expires_at = create_refresh_token(subject)
        self._main_session.add(
            RefreshToken(user_id=user.id, jti=jti, expires_at=expires_at)
        )
        await self._main_session.flush()
        return TokenResponse(
            access_token=create_access_token(subject, extra_claims={"role": role_code}),
            refresh_token=refresh,
        )

    async def _get_active_refresh(self, refresh_token: str) -> RefreshToken:
        try:
            payload = decode_token(refresh_token)
        except Exception as exc:
            raise UnauthorizedError("Невалидный refresh-токен") from exc

        if payload.get("type") != TOKEN_TYPE_REFRESH:
            raise UnauthorizedError("Ожидается refresh-токен")

        jti = payload.get("jti")
        if not jti:
            raise UnauthorizedError("Невалидный refresh-токен")

        result = await self._main_session.execute(
            select(RefreshToken).where(RefreshToken.jti == jti)
        )
        stored = result.scalar_one_or_none()
        now = datetime.now(UTC)
        if stored is None or stored.revoked_at is not None or stored.expires_at < now:
            raise UnauthorizedError("Refresh-токен отозван или истёк")
        return stored

    def _user_options(self):
        return (selectinload(User.position), selectinload(User.department))

    async def _get_user_by_email(self, email: str) -> User | None:
        result = await self._main_session.execute(
            select(User).options(*self._user_options()).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def _get_user_by_id(self, user_id: int) -> User | None:
        result = await self._main_session.execute(
            select(User).options(*self._user_options()).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
