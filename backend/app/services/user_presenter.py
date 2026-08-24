"""Утилиты для построения user-ответов API."""

from app.core.permissions import ROLE_PERMISSIONS
from app.core.rbac import get_user_role_code
from app.models.main.user import User
from app.schemas.dictionary import DictionaryItem
from app.schemas.user import UserMeRead, UserRead


def build_user_read(user: User) -> UserRead:
    return UserRead(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        birth_date=user.birth_date,
        city=user.city,
        hire_date=user.hire_date,
        department_id=user.department_id,
        position_id=user.position_id,
        role=get_user_role_code(user),
        is_blocked=user.is_blocked,
        blocked_at=user.blocked_at,
        block_reason=user.block_reason,
        department=DictionaryItem.model_validate(user.department) if user.department else None,
        position=DictionaryItem.model_validate(user.position) if user.position else None,
    )


def build_user_me_read(user: User) -> UserMeRead:
    role_code = get_user_role_code(user)
    permissions = sorted(p.value for p in ROLE_PERMISSIONS.get(role_code, frozenset()))
    base = build_user_read(user)
    return UserMeRead(**base.model_dump(), permissions=permissions)
