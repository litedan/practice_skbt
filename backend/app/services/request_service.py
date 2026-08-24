"""
Сервис кадровых заявок.

Сотрудник создаёт заявку (Создана).
HR проверяет (На проверке) и отправляет руководителю (На согласовании).
Руководитель согласовывает (Одобрена) или отклоняет.
"""

import uuid
from pathlib import Path

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, selectinload

from app.core.config import get_settings
from app.core.exceptions import AppError, ForbiddenError, NotFoundError
from app.core.permissions import Permission, RoleCode
from app.core.rbac import get_user_role_code, has_permission
from app.core.request_constants import (
    ALLOWED_STATUS_TRANSITIONS,
    ALLOWED_UPLOAD_EXTENSIONS,
    MAX_UPLOAD_SIZE_BYTES,
    UPLOADABLE_STATUSES,
    RequestStatusName,
)
from app.models.main.document_file import DocumentFile
from app.models.main.position import Position
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
            pass
        elif has_permission(current_user, Permission.REQUESTS_READ_DEPARTMENT):
            employee = aliased(User)
            query = query.join(employee, Request.employee_id == employee.id).where(
                or_(
                    employee.department_id == current_user.department_id,
                    Request.approver_id == current_user.id,
                    Request.employee_id == current_user.id,
                )
            )
        elif has_permission(current_user, Permission.REQUESTS_READ_SELF):
            query = query.where(Request.employee_id == current_user.id)
        else:
            raise ForbiddenError("Нет прав на просмотр заявок")

        if status_id is not None:
            query = query.where(Request.status_id == status_id)
        if request_type_id is not None:
            query = query.where(Request.request_type_id == request_type_id)

        result = await self._session.execute(query.offset(skip).limit(limit))
        return [RequestRead.model_validate(r) for r in result.unique().scalars()]

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
        created = await self._get_status_by_name(RequestStatusName.CREATED)

        request = Request(
            comment=payload.comment,
            employee_id=current_user.id,
            status_id=created.id,
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
            new_data={"status_id": created.id, "request_type_id": payload.request_type_id},
            ip_address=ip_address,
            user_agent=user_agent,
        )

        request_type = await self._session.get(RequestType, payload.request_type_id)
        type_name = request_type.name if request_type else "Заявка"
        await self._notifications.notify_hr_users(
            hr_user_ids=await self._get_user_ids_by_position("HR"),
            title="Новая заявка",
            message=f"{current_user.full_name} подал(а) заявку «{type_name}» (#{request.id})",
            request_id=request.id,
        )

        return RequestRead.model_validate(await self._get_request_or_404(request.id))

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

        is_owner = request.employee_id == current_user.id
        is_hr = has_permission(current_user, Permission.REQUESTS_REVIEW)
        is_manager = has_permission(current_user, Permission.REQUESTS_APPROVE)

        if not (is_owner or is_hr or is_manager):
            raise ForbiddenError("Нет прав на изменение заявки")

        if is_owner and not (is_hr or is_manager):
            if set(update_data) - {"comment"}:
                raise ForbiddenError("Сотрудник может изменить только комментарий")
            current_status = await self._session.get(Status, request.status_id)
            if current_status is None or current_status.name != RequestStatusName.CREATED:
                raise ForbiddenError("Изменения доступны только для заявки в статусе «Создана»")

        if "reviewer_id" in update_data and not is_hr:
            raise ForbiddenError("Только HR может назначать проверяющего")
        if "approver_id" in update_data and not (is_hr or is_manager):
            raise ForbiddenError("Назначать согласующего может HR или руководитель")

        if "status_id" in update_data and update_data["status_id"] is not None:
            to_status = await self._session.get(Status, update_data["status_id"])
            if to_status is None:
                raise NotFoundError("Статус не найден")
            await self._validate_status_transition(
                request.status_id, to_status, current_user, request
            )
            if to_status.name == RequestStatusName.IN_REVIEW:
                update_data.setdefault("reviewer_id", current_user.id)
            if to_status.name == RequestStatusName.APPROVED:
                update_data.setdefault("approver_id", current_user.id)

        for field, value in update_data.items():
            setattr(request, field, value)

        await self._session.flush()

        if "status_id" in update_data:
            new_status = await self._session.get(Status, request.status_id)
            status_name = new_status.name if new_status else "обновлён"
            await self._notifications.create(
                user_id=request.employee_id,
                title="Статус заявки изменён",
                message=f"Заявка #{request.id}: статус «{status_name}»",
                request_id=request.id,
            )
            if new_status and new_status.name == RequestStatusName.IN_APPROVAL:
                manager_ids = await self._get_user_ids_by_position(
                    "Руководитель",
                    department_id=request.employee.department_id if request.employee else None,
                )
                await self._notifications.notify_hr_users(
                    hr_user_ids=manager_ids,
                    title="Заявка на согласовании",
                    message=f"Заявка #{request.id} ожидает согласования руководителя",
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
        return RequestRead.model_validate(await self._get_request_or_404(request.id))

    async def get_hr_stats(self, *, current_user: User) -> RequestStatsRead:
        if not (
            has_permission(current_user, Permission.REQUESTS_READ_ANY)
            or has_permission(current_user, Permission.REQUESTS_READ_DEPARTMENT)
        ):
            raise ForbiddenError("Статистика недоступна")

        counts: dict[str, int] = {name.value: 0 for name in RequestStatusName}
        query = select(Request.status_id, func.count(Request.id)).group_by(Request.status_id)

        if has_permission(current_user, Permission.REQUESTS_READ_DEPARTMENT) and not has_permission(
            current_user, Permission.REQUESTS_READ_ANY
        ):
            query = (
                select(Request.status_id, func.count(Request.id))
                .join(User, User.id == Request.employee_id)
                .where(User.department_id == current_user.department_id)
                .group_by(Request.status_id)
            )

        result = await self._session.execute(query)
        for status_id, count in result.all():
            status = await self._session.get(Status, status_id)
            if status and status.name in counts:
                counts[status.name] = count

        return RequestStatsRead(
            total=sum(counts.values()),
            created=counts[RequestStatusName.CREATED],
            in_review=counts[RequestStatusName.IN_REVIEW],
            in_approval=counts[RequestStatusName.IN_APPROVAL],
            approved=counts[RequestStatusName.APPROVED],
            rejected=counts[RequestStatusName.REJECTED],
            closed=counts[RequestStatusName.CLOSED],
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
        if request.employee_id != current_user.id:
            raise ForbiddenError("Загружать файлы может только автор заявки")

        current_status = await self._session.get(Status, request.status_id)
        if current_status is None or current_status.name not in {s.value for s in UPLOADABLE_STATUSES}:
            raise AppError("Загрузка файлов недоступна для текущего статуса заявки")

        if len(content) > MAX_UPLOAD_SIZE_BYTES:
            raise AppError(f"Файл превышает лимит {MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)} MB")

        suffix = Path(filename).suffix.lower()
        if suffix not in ALLOWED_UPLOAD_EXTENSIONS:
            raise AppError(
                f"Недопустимый формат файла. Разрешены: {', '.join(sorted(ALLOWED_UPLOAD_EXTENSIONS))}"
            )

        upload_root = Path(settings.upload_dir) / "requests" / str(request_id)
        upload_root.mkdir(parents=True, exist_ok=True)
        file_path = upload_root / f"{uuid.uuid4().hex}{suffix}"
        file_path.write_bytes(content)

        doc = DocumentFile(name=filename, file_path=str(file_path), request_id=request_id)
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

    def _base_query(self):
        return select(Request).options(
            selectinload(Request.status),
            selectinload(Request.request_type),
            selectinload(Request.employee).selectinload(User.department),
            selectinload(Request.reviewer),
            selectinload(Request.approver),
            selectinload(Request.document_files),
        )

    async def _get_request_or_404(self, request_id: int) -> Request:
        result = await self._session.execute(self._base_query().where(Request.id == request_id))
        request = result.unique().scalar_one_or_none()
        if request is None:
            raise NotFoundError("Заявка не найдена")
        return request

    def _ensure_read_access(self, user: User, request: Request) -> None:
        if request.employee_id == user.id:
            return
        if has_permission(user, Permission.REQUESTS_READ_ANY):
            return
        if has_permission(user, Permission.REQUESTS_READ_DEPARTMENT):
            employee_dept = request.employee.department_id if request.employee else None
            if employee_dept == user.department_id or request.approver_id == user.id:
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
                f"Статус «{name.value}» не найден в справочнике. Выполните миграции.",
                status_code=500,
                code="missing_status",
            )
        return status

    async def _validate_status_transition(
        self,
        from_status_id: int,
        to_status: Status,
        actor: User,
        request: Request,
    ) -> None:
        if from_status_id == to_status.id:
            return
        from_status = await self._session.get(Status, from_status_id)
        if from_status is None:
            raise NotFoundError("Статус не найден")
        try:
            from_name = RequestStatusName(from_status.name)
            to_name = RequestStatusName(to_status.name)
        except ValueError as exc:
            raise AppError("Неизвестный статус в справочнике") from exc

        if to_name not in ALLOWED_STATUS_TRANSITIONS.get(from_name, frozenset()):
            raise AppError(
                f"Переход «{from_name.value}» → «{to_name.value}» недопустим",
                code="invalid_status_transition",
            )

        role = get_user_role_code(actor)
        if to_name == RequestStatusName.REJECTED:
            if from_name == RequestStatusName.IN_APPROVAL and role != RoleCode.MANAGER:
                raise ForbiddenError("На этапе согласования отклонить может только руководитель")
            if from_name in {RequestStatusName.CREATED, RequestStatusName.IN_REVIEW} and role != RoleCode.HR:
                raise ForbiddenError("На этапе проверки отклонить может только HR")
            return

        if to_name == RequestStatusName.APPROVED and role != RoleCode.MANAGER:
            raise ForbiddenError("Согласовать заявку может только руководитель")
        if to_name in {
            RequestStatusName.IN_REVIEW,
            RequestStatusName.IN_APPROVAL,
            RequestStatusName.CREATED,
            RequestStatusName.CLOSED,
        } and role != RoleCode.HR:
            raise ForbiddenError("Этот переход доступен только HR")

        if role == RoleCode.MANAGER:
            employee_dept = request.employee.department_id if request.employee else None
            if employee_dept != actor.department_id and request.approver_id != actor.id:
                raise ForbiddenError("Руководитель может согласовывать заявки своего отдела")

    async def _get_user_ids_by_position(
        self,
        position_name: str,
        department_id: int | None = None,
    ) -> list[int]:
        query = select(User.id).join(Position, User.position_id == Position.id).where(
            Position.name == position_name
        )
        if department_id is not None:
            query = query.where(User.department_id == department_id)
        result = await self._session.execute(query)
        return list(result.scalars())

    @staticmethod
    def _request_snapshot(request: Request) -> dict:
        return {
            "status_id": request.status_id,
            "comment": request.comment,
            "reviewer_id": request.reviewer_id,
            "approver_id": request.approver_id,
            "request_type_id": request.request_type_id,
        }
