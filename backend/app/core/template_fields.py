"""
Описание полей, которые пользователь должен заполнить вручную
для каждого шаблона документа (RequestDocumentGenerator сам
подставляет ФИО, должность, организацию, руководителя и дату —
см. RequestDocumentGenerator._build_context).

Если для кода шаблона нет записи в этом словаре, форма
дополнительных полей просто не показывается — документ будет
сгенерирован только с автоматическими данными.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class TemplateField:
    key: str
    label: str
    type: str = "text"  # text | date | number | textarea
    required: bool = True


TEMPLATE_FIELDS: dict[str, list[TemplateField]] = {
    "vacation_application": [
        TemplateField(key="vacation_days", label="Количество календарных дней", type="number"),
        TemplateField(key="vacation_start", label="Дата начала отпуска", type="date"),
    ],
    "resignation_application": [
        TemplateField(key="resignation_date", label="Дата увольнения", type="date"),
    ],
    "sick_leave_application": [
        TemplateField(key="doctor_name", label="ФИО врача", type="text"),
        TemplateField(key="clinic_name", label="Наименование клиники", type="text"),
        TemplateField(key="examination_date", label="Дата осмотра", type="date"),
        TemplateField(key="sick_start", label="Больничный с", type="date"),
        TemplateField(key="sick_end", label="Больничный по", type="date"),
    ],
}


def get_template_fields(code: str) -> list[TemplateField]:
    return TEMPLATE_FIELDS.get(code, [])
