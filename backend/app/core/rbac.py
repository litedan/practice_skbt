"""Проверка прав доступа на основе RBAC."""

from app.core.exceptions import ForbiddenError
from app.core.permissions import ROLE_PERMISSIONS, Permission, RoleCode
from app.models.main.user import User


def get_user_role_code(user: User) -> RoleCode:
    """Возвращает код роли пользователя (fallback — employee)."""
    if user.role is None:
        return RoleCode.EMPLOYEE
    return RoleCode(user.role.code)


def has_permission(user: User, permission: Permission) -> bool:
    """Проверяет наличие разрешения у пользователя."""
    role_code = get_user_role_code(user)
    return permission in ROLE_PERMISSIONS.get(role_code, frozenset())


def has_any_permission(user: User, *permissions: Permission) -> bool:
    return any(has_permission(user, p) for p in permissions)


def has_role(user: User, *roles: RoleCode) -> bool:
    return get_user_role_code(user) in roles


def ensure_permission(user: User, permission: Permission) -> None:
    if not has_permission(user, permission):
        raise ForbiddenError("Недостаточно прав для выполнения операции")


def can_read_user_profile(actor: User, target_user_id: int) -> bool:
    if actor.id == target_user_id:
        return has_permission(actor, Permission.USERS_READ_SELF)
    return has_permission(actor, Permission.USERS_READ_ANY)


def can_read_private_data(actor: User, target_user_id: int) -> bool:
    if actor.id == target_user_id:
        return has_permission(actor, Permission.PRIVATE_DATA_READ_SELF)
    return has_permission(actor, Permission.PRIVATE_DATA_READ_ANY)


def can_update_private_data(actor: User, target_user_id: int) -> bool:
    if actor.id == target_user_id:
        return has_permission(actor, Permission.PRIVATE_DATA_UPDATE_SELF)
    return has_permission(actor, Permission.PRIVATE_DATA_UPDATE_ANY)
