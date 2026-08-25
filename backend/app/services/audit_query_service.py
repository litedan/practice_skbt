"""Чтение журнала аудита (LogBD)."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.log.audit_log import AuditLog
from app.schemas.audit import AuditLogRead


class AuditQueryService:
    def __init__(self, log_session: AsyncSession) -> None:
        self._log_session = log_session

    async def list_logs(
        self,
        *,
        entity_name: str | None = None,
        entity_id: int | None = None,
        user_id: int | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[AuditLogRead]:
        query = select(AuditLog).order_by(AuditLog.created_at.desc())

        if entity_name:
            query = query.where(AuditLog.entity_name == entity_name)
        if entity_id is not None:
            query = query.where(AuditLog.entity_id == entity_id)
        if user_id is not None:
            query = query.where(AuditLog.user_id == user_id)

        result = await self._log_session.execute(query.offset(skip).limit(limit))
        return [AuditLogRead.model_validate(row) for row in result.scalars()]
