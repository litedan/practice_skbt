"""Сервис аудита и логирования (LogBD)."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.log.audit_log import AuditLog
from app.models.log.auth_log import AuthLog
from app.models.log.sensitive_access_log import SensitiveAccessLog
from app.models.log.system_events_log import SystemEventsLog


class AuditService:
    """Запись событий в контур LogBD."""

    def __init__(self, log_session: AsyncSession) -> None:
        self._log_session = log_session

    async def log_auth_attempt(
        self,
        *,
        email: str,
        action: str,
        ip_address: str | None,
        user_agent: str | None,
        fail_reason: str | None = None,
    ) -> None:
        entry = AuthLog(
            email=email,
            action=action,
            fail_reason=fail_reason,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self._log_session.add(entry)

    async def log_sensitive_access(
        self,
        *,
        user_id: int,
        target_user_id: int,
        data_type: str,
        action: str,
        ip_address: str | None,
        user_agent: str | None,
    ) -> None:
        entry = SensitiveAccessLog(
            user_id=user_id,
            target_user_id=target_user_id,
            data_type=data_type,
            action=action,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self._log_session.add(entry)

    async def log_entity_change(
        self,
        *,
        entity_name: str,
        entity_id: int,
        action: str,
        user_id: int | None,
        old_data: dict | None,
        new_data: dict | None,
        ip_address: str | None,
        user_agent: str | None,
    ) -> None:
        entry = AuditLog(
            entity_name=entity_name,
            entity_id=entity_id,
            action=action,
            user_id=user_id,
            old_data=old_data,
            new_data=new_data,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self._log_session.add(entry)

    async def log_system_event(
        self,
        *,
        endpoint: str | None,
        error_message: str,
        stack_trace: str | None,
        event_type: str,
    ) -> None:
        entry = SystemEventsLog(
            endpoint=endpoint,
            error_message=error_message,
            stack_trace=stack_trace,
            event_type=event_type,
        )
        self._log_session.add(entry)
