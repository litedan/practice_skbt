"""
Описание полей, которые пользователь должен заполнить вручную
для каждого шаблона документа (RequestDocumentGenerator сам
подставляет ФИО, должность, организацию, руководителя и дату —
см. RequestDocumentGenerator._build_context).

Переменные которые пользователю надо будет заполнить выносятся из документа автоматичеки.
При заполнении шаблона важно чтобы переменная была с _ вместо пробелов, он будет заменен на пробел после
"""
from __future__ import annotations

import re
import zipfile
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from app.core.config import get_settings


@dataclass(frozen=True)
class TemplateField:
    key: str
    label: str
    type: str = "text"  # text | date | number | textarea
    required: bool = True


# Переменные, которые RequestDocumentGenerator._build_context подставляет сам 
AUTO_CONTEXT_KEYS = {
    "employee_full_name",
    "employee_position",
    "position",
    "organization_name",
    "director_name",
    "director_position",
    "today",
    "request_id",
}

_PLACEHOLDER_RE = re.compile(r"\{\{\s*([^\s{}|]+)\s*(?:\|[^}]*)?\}\}")
_TAG_RE = re.compile(r"<[^>]+>")

_DATE_HINTS = ("дата", "дате", "срок")
_NUMBER_HINTS = ("количество", "число", "сумма", "стаж", "номер", "возраст", "дней", "лет", "оклад")


def _guess_type(key: str) -> str:
    lowered = key.lower()
    if any(hint in lowered for hint in _DATE_HINTS):
        return "date"
    if any(hint in lowered for hint in _NUMBER_HINTS):
        return "number"
    return "text"


def _humanize_label(key: str) -> str:
    return key.replace("_", " ").strip()


def _extract_variables(docx_path: Path) -> list[str]:
    with zipfile.ZipFile(docx_path) as zf:
        xml = zf.read("word/document.xml").decode("utf-8", errors="ignore")
    text = _TAG_RE.sub("", xml)
    seen: list[str] = []
    for match in _PLACEHOLDER_RE.finditer(text):
        var = match.group(1)
        if var not in seen:
            seen.append(var)
    return seen


@lru_cache(maxsize=64)
def _cached_fields(path_str: str, mtime_ns: int) -> tuple[TemplateField, ...]:
    """
    если файл шаблона перезаписали новой
    версией, кэш сам инвалидируется без перезапуска бэкенда.
    """
    variables = _extract_variables(Path(path_str))
    fields = [
        TemplateField(key=var, label=_humanize_label(var), type=_guess_type(var))
        for var in variables
        if var not in AUTO_CONTEXT_KEYS
    ]
    return tuple(fields)


def resolve_template_path(file_path: str) -> Path:
    """
    Приводит templates.file_path (может быть как относительным, так и
    абсолютным) к реальному пути на диске.
    """
    path = Path(file_path)
    if path.is_absolute():
        return path
    return Path(get_settings().document_templates_dir) / path


def get_template_fields(file_path: Path | str) -> list[TemplateField]:
    """
    Поля формы для шаблона по пути к .docx

    Если файл не найден или его не удалось прочитать - форма не покажет поля, чтобы одна
    сломанная переменная не роняла весь список шаблонов.
    """
    path = Path(file_path)
    try:
        mtime_ns = path.stat().st_mtime_ns
    except OSError:
        return []

    try:
        return list(_cached_fields(str(path), mtime_ns))
    except (KeyError, zipfile.BadZipFile, OSError):
        return []
