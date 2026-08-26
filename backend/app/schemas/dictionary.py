"""Схемы справочников."""

from app.schemas.common import ORMModel


class DictionaryItem(ORMModel):
    id: int
    name: str


class RequestTypeItem(DictionaryItem):
    file_path: str | None = None


class TemplateFieldItem(ORMModel):
    key: str
    label: str
    type: str = "text"
    required: bool = True


class TemplateItem(ORMModel):
    id: int
    name: str
    code: str
    fields: list[TemplateFieldItem] = []
