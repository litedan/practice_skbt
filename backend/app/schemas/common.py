"""Общие схемы ответов API."""

from pydantic import BaseModel, ConfigDict


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
