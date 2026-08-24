"""Схемы пользователя."""

from datetime import date

from pydantic import EmailStr

from app.core.permissions import RoleCode
from app.schemas.common import ORMModel
from app.schemas.dictionary import DictionaryItem


class UserBase(ORMModel):
    email: EmailStr | None = None
    full_name: str
    phone: str | None = None
    birth_date: date | None = None
    city: str | None = None
    hire_date: date | None = None
    department_id: int | None = None
    position_id: int | None = None


class UserRead(UserBase):
    id: int
    role: RoleCode
    is_blocked: bool
    blocked_at: date | None = None
    block_reason: str | None = None
    department: DictionaryItem | None = None
    position: DictionaryItem | None = None


class UserMeRead(UserRead):
    permissions: list[str]
