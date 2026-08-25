"""
FastAPI Dependencies.

- get_db / get_log_db  — сессии SQLAlchemy
- get_current_user     — пользователь из JWT Bearer Token
- ClientInfo           — IP и User-Agent для аудита
"""

from typing import Annotated

from fastapi import Depends, Header, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_log_session, get_main_session
from app.core.permissions import Permission
from app.core.rbac import ensure_permission
from app.models.main.user import User
from app.services.audit_query_service import AuditQueryService
from app.services.audit_service import AuditService
from app.services.auth_service import AuthService
from app.services.document_service import DocumentService
from app.services.notification_service import NotificationService
from app.services.request_service import RequestService
from app.services.user_private_data_service import UserPrivateDataService
from app.services.user_service import UserService

# --- Security scheme ---
bearer_scheme = HTTPBearer(auto_error=False)

# --- DB Sessions ---
MainDB = Annotated[AsyncSession, Depends(get_main_session)]
LogDB = Annotated[AsyncSession, Depends(get_log_session)]


def get_client_ip(request: Request) -> str | None:
    """Извлекает IP клиента (с учётом reverse-proxy)."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None


class ClientInfo:
    """Метаданные клиента для записи в логи."""

    def __init__(self, request: Request, user_agent: str | None = Header(default=None)) -> None:
        self.ip_address = get_client_ip(request)
        self.user_agent = user_agent


ClientInfoDep = Annotated[ClientInfo, Depends()]


# --- Services ---
def get_audit_service(log_db: LogDB) -> AuditService:
    return AuditService(log_db)


AuditServiceDep = Annotated[AuditService, Depends(get_audit_service)]


def get_auth_service(main_db: MainDB, audit_service: AuditServiceDep) -> AuthService:
    return AuthService(main_db, audit_service)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


def get_user_service(main_db: MainDB, audit_service: AuditServiceDep) -> UserService:
    return UserService(main_db, audit_service)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


def get_audit_query_service(log_db: LogDB) -> AuditQueryService:
    return AuditQueryService(log_db)


AuditQueryServiceDep = Annotated[AuditQueryService, Depends(get_audit_query_service)]


def get_private_data_service(
    main_db: MainDB,
    audit_service: AuditServiceDep,
) -> UserPrivateDataService:
    return UserPrivateDataService(main_db, audit_service)


PrivateDataServiceDep = Annotated[UserPrivateDataService, Depends(get_private_data_service)]


def get_notification_service(main_db: MainDB) -> NotificationService:
    return NotificationService(main_db)


NotificationServiceDep = Annotated[NotificationService, Depends(get_notification_service)]


def get_document_service() -> DocumentService:
    return DocumentService()


DocumentServiceDep = Annotated[DocumentService, Depends(get_document_service)]


def get_request_service(
    main_db: MainDB,
    audit_service: AuditServiceDep,
    notification_service: NotificationServiceDep,
) -> RequestService:
    return RequestService(main_db, audit_service, notification_service)


RequestServiceDep = Annotated[RequestService, Depends(get_request_service)]


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    auth_service: AuthServiceDep,
) -> User:
    """Dependency: текущий аутентифицированный пользователь из JWT."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        from app.core.exceptions import UnauthorizedError

        raise UnauthorizedError("Требуется Bearer Token")

    return await auth_service.get_user_from_access_token(credentials.credentials)


CurrentUser = Annotated[User, Depends(get_current_user)]


class RequirePermission:
    """Dependency: проверяет одно разрешение RBAC."""

    def __init__(self, permission: Permission) -> None:
        self.permission = permission

    async def __call__(self, current_user: CurrentUser) -> User:
        ensure_permission(current_user, self.permission)
        return current_user


def require_permission(permission: Permission) -> RequirePermission:
    return RequirePermission(permission)
