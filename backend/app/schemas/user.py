"""Схемы пользователя."""

from datetime import date

from pydantic import Field, field_validator

from app.core.permissions import RoleCode
from app.schemas.common import EmailAddress, ORMModel
from app.schemas.dictionary import DictionaryItem


class UserBase(ORMModel):
    email: EmailAddress | None = None
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


class AdminUserUpdate(ORMModel):
    """Админ: смена отдела, должности, блокировка."""

    department_id: int | None = None
    position_id: int | None = None
    is_blocked: bool | None = None
    block_reason: str | None = Field(default=None, max_length=500)


class UserMeRead(UserRead):
    permissions: list[str]


class UserProfileUpdate(ORMModel):
    """Разрешённые поля для саморедактирования профиля."""

    phone: str | None = Field(default=None, max_length=32)
    city: str | None = Field(default=None, max_length=100)
    birth_date: date | None = None


class ChangePasswordRequest(ORMModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        has_letter = any(c.isalpha() for c in value)
        has_digit = any(c.isdigit() for c in value)
        if not (has_letter and has_digit):
            raise ValueError("Пароль должен содержать буквы и цифры")
        return value
