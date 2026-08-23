"""Схемы пользователя."""

from datetime import date, datetime

from pydantic import EmailStr, Field

from app.schemas.common import ORMModel
from app.schemas.role import RoleRead


class UserBase(ORMModel):
    email: EmailStr
    full_name: str
    phone: str | None = None
    birth_date: date | None = None
    city: str | None = None
    hire_date: date | None = None
    department_id: int | None = None
    position_id: int | None = None


class UserRead(UserBase):
    id: int
    role_id: int
    role: RoleRead
    is_blocked: bool
    blocked_at: datetime | None = None
    block_reason: str | None = None


class UserMeRead(UserRead):
    """Профиль текущего пользователя (/users/me)."""

    permissions: list[str]
