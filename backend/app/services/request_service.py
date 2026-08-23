"""
Сервис кадровых заявок.

- Сотрудник: создаёт заявки, видит свои, загружает файлы
- HR: видит все, меняет статус, назначает checker
- Смена статусов логируется в Audit_log + in-app уведомления
"""

import uuid
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.core.exceptions import AppError, ForbiddenError, NotFoundError
from app.core.permissions import Permission, RoleCode
from app.core.rbac import get_user_role_code, has_permission
from app.core.request_constants import (
    ALLOWED_STATUS_TRANSITIONS,
    ALLOWED_UPLOAD_EXTENSIONS,
    MAX_UPLOAD_SIZE_BYTES,
    RequestStatusName,
)
from app.models.main.document_file import DocumentFile
from app.models.main.request import Request
from app.models.main.request_type import RequestType
from app.models.main.status import Status
from app.models.main.user import User
from app.schemas.request import (
    DocumentFileRead,
    RequestCreate,
    RequestDetailRead,
    RequestRead,
    RequestStatsRead,
    RequestUpdate,
)
from app.services.audit_service import AuditService
from app.services.notification_service import NotificationService

settings = get_settings()


class RequestService:
    def __init__(
        self,
        session: AsyncSession,
        audit_service: AuditService,
        notification_service: NotificationService,
    ) -> None:
        self._session = session
        self._audit = audit_service
        self._notifications = notification_service

    async def list_requests(
        self,
        *,
        current_user: User,
        status_id: int | None = None,
        request_type_id: int | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[RequestRead]:
        query = self._base_query().order_by(Request.created_at.desc())

        if has_permission(current_user, Permission.REQUESTS_READ_ANY):
            pass  # HR — все заявки
        elif has_permission(current_user, Permission.REQUESTS_READ_SELF):
            query = query.where(Request.creator_id == current_user.id)
        else:
            raise ForbiddenError("Нет прав на просмотр заявок")

        if status_id is not None:
            query = query.where(Request.status_id == status_id)
        if request_type_id is not None:
            query = query.where(Request.request_type_id == request_type_id)

        result = await self._session.execute(query.offset(skip).limit(limit))
        return [RequestRead.model_validate(r) for r in result.scalars()]

    async def get_request(self, *, current_user: User, request_id: int) -> RequestDetailRead:
        request = await self._get_request_or_404(request_id)
        self._ensure_read_access(current_user, request)
        return RequestDetailRead.model_validate(request)

    async def create_request(
        self,
        *,
        current_user: User,
        payload: RequestCreate,
        ip_address: str | None,
        user_agent: str | None,
    ) -> RequestRead:
        await self._ensure_request_type_exists(payload.request_type_id)
        new_status = await self._get_status_by_name(RequestStatusName.NEW)

        request = Request(
            comment=payload.comment,
            date_from=payload.date_from,
            date_to=payload.date_to,
            creator_id=current_user.id,
            status_id=new_status.id,
            request_type_id=payload.request_type_id,
        )
        self._session.add(request)
        await self._session.flush()

        await self._audit.log_entity_change(
            entity_name="requests",
            entity_id=request.id,
            action="create",
            user_id=current_user.id,
            old_data=None,
            new_data={
                "status_id": new_status.id,
                "request_type_id": payload.request_type_id,
                "date_from": payload.date_from.isoformat() if payload.date_from else None,
                "date_to": payload.date_to.isoformat() if payload.date_to else None,
            },
            ip_address=ip_address,
            user_agent=user_agent,
        )

        hr_ids = await self._get_hr_user_ids()
        request_type = await self._session.get(RequestType, payload.request_type_id)
        type_name = request_type.name if request_type else "Заявка"
        await self._notifications.notify_hr_users(
            hr_user_ids=hr_ids,
            title="Новая заявка",
            message=f"{current_user.full_name} подал(а) заявку «{type_name}» (#{request.id})",
            request_id=request.id,
        )

        loaded = await self._get_request_or_404(request.id)
        return RequestRead.model_validate(loaded)

    async def update_request(
        self,
        *,
        current_user: User,
        request_id: int,
        payload: RequestUpdate,
        ip_address: str | None,
        user_agent: str | None,
    ) -> RequestRead:
        request = await self._get_request_or_404(request_id)
        old_data = self._request_snapshot(request)
        update_data = payload.model_dump(exclude_unset=True)

        is_hr = has_permission(current_user, Permission.REQUESTS_UPDATE_STATUS)
        is_owner = request.creator_id == current_user.id

        if not is_hr and not is_owner:
            raise ForbiddenError("Нет прав на изменение заявки")

        # Сотрудник может менять comment и даты своей заявки в статусе «Новая»
        if is_owner and not is_hr:
            allowed_fields = {"comment", "date_from", "date_to"}
            if set(update_data) - allowed_fields:
                raise ForbiddenError("Сотрудник может изменить только комментарий и даты")
            current_status = await self._session.get(Status, request.status_id)
            if current_status is None or current_status.name != RequestStatusName.NEW:
                raise ForbiddenError("Изменения доступны только для новой заявки")

        if "date_from" in update_data or "date_to" in update_data:
            merged_from = update_data.get("date_from", request.date_from)
            merged_to = update_data.get("date_to", request.date_to)
            self._validate_date_range(merged_from, merged_to)

        if "status_id" in update_data and update_data["status_id"] is not None:
            if not is_hr:
                raise ForbiddenError("Только HR может менять статус заявки")
            await self._validate_status_transition(request.status_id, update_data["status_id"])
            if update_data.get("checker_id") is None and current_user.id:
                update_data.setdefault("checker_id", current_user.id)

        if "checker_id" in update_data and update_data["checker_id"] is not None and not is_hr:
            raise ForbiddenError("Только HR может назначать проверяющего")

        for field, value in update_data.items():
            setattr(request, field, value)

        await self._session.flush()

        if "status_id" in update_data:
            new_status = await self._session.get(Status, request.status_id)
            status_name = new_status.name if new_status else "обновлён"
            await self._notifications.create(
                user_id=request.creator_id,
                title="Статус заявки изменён",
                message=f"Заявка #{request.id}: статус «{status_name}»",
                request_id=request.id,
            )

        await self._audit.log_entity_change(
            entity_name="requests",
            entity_id=request.id,
            action="update",
            user_id=current_user.id,
            old_data=old_data,
            new_data=self._request_snapshot(request),
            ip_address=ip_address,
            user_agent=user_agent,
        )

        loaded = await self._get_request_or_404(request.id)
        return RequestRead.model_validate(loaded)

    async def get_hr_stats(self, *, current_user: User) -> RequestStatsRead:
        if not has_permission(current_user, Permission.REQUESTS_READ_ANY):
            raise ForbiddenError("Статистика доступна только HR")

        status_map = await self._get_status_map()
        counts: dict[str, int] = {name.value: 0 for name in RequestStatusName}

        result = await self._session.execute(
            select(Request.status_id, func.count(Request.id)).group_by(Request.status_id)
        )
        for status_id, count in result.all():
            status = await self._session.get(Status, status_id)
            if status and status.name in counts:
                counts[status.name] = count

        return RequestStatsRead(
            total=sum(counts.values()),
            new=counts[RequestStatusName.NEW],
            in_progress=counts[RequestStatusName.IN_PROGRESS],
            approved=counts[RequestStatusName.APPROVED],
            rejected=counts[RequestStatusName.REJECTED],
        )

    async def upload_file(
        self,
        *,
        current_user: User,
        request_id: int,
        filename: str,
        content: bytes,
    ) -> DocumentFileRead:
        request = await self._get_request_or_404(request_id)
        if request.creator_id != current_user.id:
            raise ForbiddenError("Загружать файлы может только автор заявки")

        current_status = await self._session.get(Status, request.status_id)
        if current_status is None or current_status.name not in (
            RequestStatusName.NEW,
            RequestStatusName.IN_PROGRESS,
        ):
            raise AppError("Загрузка файлов недоступна для текущего статуса заявки")

        if len(content) > MAX_UPLOAD_SIZE_BYTES:
            raise AppError(f"Файл превышает лимит {MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)} MB")

        suffix = Path(filename).suffix.lower()
        if suffix not in ALLOWED_UPLOAD_EXTENSIONS:
            raise AppError(f"Недопустимый формат файла. Разрешены: {', '.join(sorted(ALLOWED_UPLOAD_EXTENSIONS))}")

        upload_root = Path(settings.upload_dir) / "requests" / str(request_id)
        upload_root.mkdir(parents=True, exist_ok=True)

        stored_name = f"{uuid.uuid4().hex}{suffix}"
        file_path = upload_root / stored_name
        file_path.write_bytes(content)

        doc = DocumentFile(
            name=filename,
            file_path=str(file_path),
            request_id=request_id,
        )
        self._session.add(doc)
        await self._session.flush()

        return DocumentFileRead.model_validate(doc)

    async def list_files(self, *, current_user: User, request_id: int) -> list[DocumentFileRead]:
        request = await self._get_request_or_404(request_id)
        self._ensure_read_access(current_user, request)
        return [DocumentFileRead.model_validate(f) for f in request.document_files]

    async def get_file_for_download(
        self,
        *,
        current_user: User,
        request_id: int,
        file_id: int,
    ) -> tuple[DocumentFile, Path]:
        request = await self._get_request_or_404(request_id)
        self._ensure_read_access(current_user, request)

        doc = next((f for f in request.document_files if f.id == file_id), None)
        if doc is None:
            raise NotFoundError("Файл не найден")

        path = Path(doc.file_path)
        if not path.is_file():
            raise NotFoundError("Файл отсутствует на диске")

        return doc, path

    # --- private helpers ---

    def _base_query(self):
        return select(Request).options(
            selectinload(Request.status),
            selectinload(Request.request_type),
            selectinload(Request.creator),
            selectinload(Request.checker),
            selectinload(Request.document_files),
        )

    async def _get_request_or_404(self, request_id: int) -> Request:
        result = await self._session.execute(
            self._base_query().where(Request.id == request_id)
        )
        request = result.scalar_one_or_none()
        if request is None:
            raise NotFoundError("Заявка не найдена")
        return request

    def _ensure_read_access(self, user: User, request: Request) -> None:
        if request.creator_id == user.id and has_permission(user, Permission.REQUESTS_READ_SELF):
            return
        if has_permission(user, Permission.REQUESTS_READ_ANY):
            return
        raise ForbiddenError("Нет доступа к этой заявке")

    async def _ensure_request_type_exists(self, request_type_id: int) -> None:
        if await self._session.get(RequestType, request_type_id) is None:
            raise NotFoundError("Тип заявки не найден")

    async def _get_status_by_name(self, name: RequestStatusName) -> Status:
        result = await self._session.execute(select(Status).where(Status.name == name.value))
        status = result.scalar_one_or_none()
        if status is None:
            raise AppError(
                f"Статус «{name.value}» не найден в справочнике. Выполните миграции/seed.",
                status_code=500,
                code="missing_status",
            )
        return status

    async def _get_status_map(self) -> dict[str, Status]:
        result = await self._session.execute(select(Status))
        return {s.name: s for s in result.scalars()}

    async def _validate_status_transition(self, from_status_id: int, to_status_id: int) -> None:
        if from_status_id == to_status_id:
            return

        from_status = await self._session.get(Status, from_status_id)
        to_status = await self._session.get(Status, to_status_id)
        if from_status is None or to_status is None:
            raise NotFoundError("Статус не найден")

        try:
            from_name = RequestStatusName(from_status.name)
            to_name = RequestStatusName(to_status.name)
        except ValueError as exc:
            raise AppError("Неизвестный статус в справочнике") from exc

        allowed = ALLOWED_STATUS_TRANSITIONS.get(from_name, frozenset())
        if to_name not in allowed:
            raise AppError(
                f"Переход «{from_name.value}» → «{to_name.value}» недопустим",
                code="invalid_status_transition",
            )

    async def _get_hr_user_ids(self) -> list[int]:
        from app.models.main.role import Role

        result = await self._session.execute(
            select(User.id)
            .join(Role, User.role_id == Role.id)
            .where(Role.code == RoleCode.HR)
        )
        return list(result.scalars())

    @staticmethod
    def _validate_date_range(date_from, date_to) -> None:
        if (date_from is None) ^ (date_to is None):
            raise AppError("date_from и date_to должны быть указаны вместе")
        if date_from is not None and date_to is not None and date_from > date_to:
            raise AppError("date_from не может быть позже date_to")

    @staticmethod
    def _request_snapshot(request: Request) -> dict:
        return {
            "status_id": request.status_id,
            "comment": request.comment,
            "date_from": request.date_from.isoformat() if request.date_from else None,
            "date_to": request.date_to.isoformat() if request.date_to else None,
            "checker_id": request.checker_id,
            "request_type_id": request.request_type_id,
        }
