"""Общие схемы ответов API."""

import re
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict

# EmailStr отклоняет спец. домены (.local, .test). Для КЭДО/dev допускаем их.
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _validate_email(value: str) -> str:
    email = value.strip()
    if not _EMAIL_RE.match(email):
        raise ValueError("Некорректный email")
    return email.lower()


EmailAddress = Annotated[str, AfterValidator(_validate_email)]


class ORMModel(BaseModel):
    """Базовая схема с поддержкой ORM-объектов."""

    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    detail: str


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    size: int
