"""Схемы справочников."""

from app.schemas.common import ORMModel


class DictionaryItem(ORMModel):
    id: int
    name: str


class RequestTypeItem(DictionaryItem):
    file_path: str | None = None
