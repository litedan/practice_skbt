"""Админ-эндпоинты: аудит, управление пользователями."""



from typing import Annotated



from fastapi import APIRouter, Depends, Query



from app.api.deps import AuditQueryServiceDep, ClientInfoDep, UserServiceDep, require_permission

from app.core.permissions import Permission

from app.models.main.user import User

from app.schemas.audit import AuditLogRead

from app.schemas.user import AdminUserUpdate, UserRead

from app.services.user_presenter import build_user_read



router = APIRouter(prefix="/admin", tags=["Admin"])





@router.get("/audit", response_model=list[AuditLogRead])

async def list_audit_logs(

    _: Annotated[User, Depends(require_permission(Permission.AUDIT_READ))],

    service: AuditQueryServiceDep,

    entity_name: str | None = Query(default=None),

    entity_id: int | None = Query(default=None),

    user_id: int | None = Query(default=None),

    skip: int = Query(default=0, ge=0),

    limit: int = Query(default=50, ge=1, le=200),

) -> list[AuditLogRead]:

    """Журнал изменений сущностей (LogBD). Только admin."""

    return await service.list_logs(

        entity_name=entity_name,

        entity_id=entity_id,

        user_id=user_id,

        skip=skip,

        limit=limit,

    )





@router.get("/users", response_model=list[UserRead])

async def list_users(

    _: Annotated[User, Depends(require_permission(Permission.USERS_READ_ANY))],

    user_service: UserServiceDep,

    department_id: int | None = Query(default=None),

    position_id: int | None = Query(default=None),

    search: str | None = Query(default=None, description="Поиск по ФИО или email"),

    skip: int = Query(default=0, ge=0),

    limit: int = Query(default=50, ge=1, le=200),

) -> list[UserRead]:

    """Список пользователей для админ-панели."""

    users = await user_service.list_users(

        department_id=department_id,

        position_id=position_id,

        search=search,

        skip=skip,

        limit=limit,

    )

    return [build_user_read(user) for user in users]





@router.patch("/users/{user_id}", response_model=UserRead)

async def update_user(

    user_id: int,

    payload: AdminUserUpdate,

    current_user: Annotated[User, Depends(require_permission(Permission.USERS_UPDATE_ANY))],

    user_service: UserServiceDep,

    client: ClientInfoDep,

) -> UserRead:

    """Изменение отдела, должности, блокировки пользователя."""

    user = await user_service.admin_update_user(

        user_id=user_id,

        payload=payload,

        actor_id=current_user.id,

        ip_address=client.ip_address,

        user_agent=client.user_agent,

    )

    return build_user_read(user)

