"""
RBAC КЭДО. Роль определяется должностью (positions.name):
- Работник → employee
- HR → hr
- Руководитель → manager
- Администратор → admin
"""

from enum import StrEnum


class RoleCode(StrEnum):
    EMPLOYEE = "employee"
    HR = "hr"
    MANAGER = "manager"
    ADMIN = "admin"


POSITION_TO_ROLE: dict[str, RoleCode] = {
    "Работник": RoleCode.EMPLOYEE,
    "HR": RoleCode.HR,
    "Руководитель": RoleCode.MANAGER,
    "Администратор": RoleCode.ADMIN,
}


class Permission(StrEnum):
    USERS_READ_SELF = "users:read_self"
    USERS_READ_DEPARTMENT = "users:read_department"
    USERS_READ_ANY = "users:read_any"
    USERS_BLOCK = "users:block"
    USERS_UPDATE_ANY = "users:update_any"

    PRIVATE_DATA_READ_SELF = "private_data:read_self"
    PRIVATE_DATA_UPDATE_SELF = "private_data:update_self"
    PRIVATE_DATA_READ_ANY = "private_data:read_any"
    PRIVATE_DATA_UPDATE_ANY = "private_data:update_any"

    REQUESTS_CREATE = "requests:create"
    REQUESTS_READ_SELF = "requests:read_self"
    REQUESTS_READ_DEPARTMENT = "requests:read_department"
    REQUESTS_READ_ANY = "requests:read_any"
    REQUESTS_REVIEW = "requests:review"
    REQUESTS_APPROVE = "requests:approve"

    NOTIFICATIONS_READ_SELF = "notifications:read_self"
    NOTIFICATIONS_MARK_READ_SELF = "notifications:mark_read_self"

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
            Permission.REQUESTS_REVIEW,
            Permission.NOTIFICATIONS_READ_SELF,
            Permission.NOTIFICATIONS_MARK_READ_SELF,
            Permission.DICTIONARIES_READ,
        }
    ),
    RoleCode.MANAGER: frozenset(
        {
            Permission.USERS_READ_SELF,
            Permission.USERS_READ_DEPARTMENT,
            Permission.PRIVATE_DATA_READ_SELF,
            Permission.REQUESTS_CREATE,
            Permission.REQUESTS_READ_SELF,
            Permission.REQUESTS_READ_DEPARTMENT,
            Permission.REQUESTS_APPROVE,
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
            Permission.USERS_UPDATE_ANY,
            Permission.DICTIONARIES_READ,
            Permission.AUDIT_READ,
            Permission.SYSTEM_MONITOR,
        }
    ),
}
