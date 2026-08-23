"""
RBAC: роли и разрешения КЭДО.

Роли:
- employee — сотрудник (свои заявки, профиль, ПД)
- hr       — HR-специалист (все заявки, ПД сотрудников, смена статусов)
- admin    — администратор системы (мониторинг, блокировка, без доступа к ПД)
"""

from enum import StrEnum


class RoleCode(StrEnum):
    EMPLOYEE = "employee"
    HR = "hr"
    ADMIN = "admin"


class Permission(StrEnum):
    # Пользователи
    USERS_READ_SELF = "users:read_self"
    USERS_READ_ANY = "users:read_any"
    USERS_BLOCK = "users:block"

    # Персональные данные
    PRIVATE_DATA_READ_SELF = "private_data:read_self"
    PRIVATE_DATA_UPDATE_SELF = "private_data:update_self"
    PRIVATE_DATA_READ_ANY = "private_data:read_any"
    PRIVATE_DATA_UPDATE_ANY = "private_data:update_any"

    # Заявки
    REQUESTS_CREATE = "requests:create"
    REQUESTS_READ_SELF = "requests:read_self"
    REQUESTS_READ_ANY = "requests:read_any"
    REQUESTS_UPDATE_STATUS = "requests:update_status"

    # Уведомления
    NOTIFICATIONS_READ_SELF = "notifications:read_self"
    NOTIFICATIONS_MARK_READ_SELF = "notifications:mark_read_self"

    # Справочники и система
    DICTIONARIES_READ = "dictionaries:read"
    AUDIT_READ = "audit:read"
    SYSTEM_MONITOR = "system:monitor"


ROLE_PERMISSIONS: dict[RoleCode, frozenset[Permission]] = {
    RoleCode.EMPLOYEE: frozenset(
        {
            Permission.USERS_READ_SELF,
            Permission.PRIVATE_DATA_READ_SELF,
            Permission.PRIVATE_DATA_UPDATE_SELF,
            Permission.REQUESTS_CREATE,
            Permission.REQUESTS_READ_SELF,
            Permission.NOTIFICATIONS_READ_SELF,
            Permission.NOTIFICATIONS_MARK_READ_SELF,
            Permission.DICTIONARIES_READ,
        }
    ),
    RoleCode.HR: frozenset(
        {
            Permission.USERS_READ_SELF,
            Permission.USERS_READ_ANY,
            Permission.PRIVATE_DATA_READ_SELF,
            Permission.PRIVATE_DATA_UPDATE_SELF,
            Permission.PRIVATE_DATA_READ_ANY,
            Permission.PRIVATE_DATA_UPDATE_ANY,
            Permission.REQUESTS_CREATE,
            Permission.REQUESTS_READ_SELF,
            Permission.REQUESTS_READ_ANY,
            Permission.REQUESTS_UPDATE_STATUS,
            Permission.NOTIFICATIONS_READ_SELF,
            Permission.NOTIFICATIONS_MARK_READ_SELF,
            Permission.DICTIONARIES_READ,
        }
    ),
    RoleCode.ADMIN: frozenset(
        {
            Permission.USERS_READ_SELF,
            Permission.USERS_READ_ANY,
            Permission.USERS_BLOCK,
            Permission.DICTIONARIES_READ,
            Permission.AUDIT_READ,
            Permission.SYSTEM_MONITOR,
        }
    ),
}
