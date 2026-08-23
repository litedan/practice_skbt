"""Схемы ролей."""

from app.schemas.common import ORMModel


class RoleRead(ORMModel):
    id: int
    code: str
    name: str
