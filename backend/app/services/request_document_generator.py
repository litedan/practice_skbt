import uuid
from datetime import date
from pathlib import Path
from typing import Any, Optional

from docxtpl import DocxTemplate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.config import get_settings
from app.models.main.document_file import DocumentFile
from app.models.main.request import Request
from app.models.main.template import Template
from app.models.main.user import User


settings = get_settings()


class RequestDocumentGenerator:
    """
    Генератор документов, связанных с заявками.

    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def generate(
        self,
        employee_id: int,
        template_code: str,
        context: dict[str, Any],
        request_id: int,
    ) -> DocumentFile:
        """
        Генерирует документ и прикрепляет его к заявке.

        """

        # Получаем сотрудника
        result = await self.session.execute(
            select(User)
            .options(selectinload(User.position))
            .where(User.id == employee_id)
        )
        employee = result.scalar_one_or_none()

        if employee is None:
            raise ValueError(
                f"Сотрудник с id={employee_id} не найден"
            )


        # Получаем заявку
        request = await self.session.get(
            Request,
            request_id,
        )

        if request is None:
            raise ValueError(
                f"Заявка с id={request_id} не найдена"
            )


        # Проверяем что заявка принадлежит сотруднику
        if request.employee_id != employee_id:
            raise ValueError(
                "Указанная заявка не принадлежит сотруднику"
            )


        #получаем шаблон
        result = await self.session.execute(
            select(Template).where(
                Template.code == template_code,
                Template.is_active.is_(True),
            )
        )

        template = result.scalar_one_or_none()

        if template is None:
            raise ValueError(
                f"Шаблон '{template_code}' не найден"
            )

        template_path = self._get_template_path(
            template,
        )

        if not template_path.exists():
            raise FileNotFoundError(
                f"Файл шаблона не найден: {template_path}"
            )


        # Формируем контекст


        render_context = self._build_context(
            employee=employee,
            request=request,
            context=context,
        )
        
        # Создаем папку для сгенеренных док-ов если еще нет.


        output_dir = Path(
            settings.generated_documents_dir
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        # формирование имени файла

        file_name = self._build_file_name(
            template_code=template_code,
            request_id=request_id,
        )

        output_path = output_dir / file_name

        # Генерим документ

        document = DocxTemplate(
            str(template_path)
        )

        document.render(
            render_context
        )

        document.save(
            str(output_path)
        )

        # Создаем документ

        document_file = DocumentFile(
            name=file_name,
            request_id=request_id,
            file_path=str(output_path),
        )

        self.session.add(
            document_file
        )

        await self.session.flush()


        return document_file

    def _get_template_path(
        self,
        template: Template,
    ) -> Path:
        """
        Определяет путь к шаблону.

        В БД templates.file_path храним, например:

            zayavlenie_na_otpusk.docx

        Фактический путь:

            ./app/templates/zayavlenie_na_otpusk.docx
        """

        file_path = Path(
            template.file_path
        )

        if file_path.is_absolute():
            return file_path

        return (
            Path(settings.document_templates_dir)
            / file_path
        )

    def _build_context(
        self,
        *,
        employee: User,
        request: Request,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Добавляет общие данные к данным,
        переданным конкретным типом документа.

        Пользовательский context не удаляется.
        """

        result_context = dict(context)

        # Общие данные сотрудника
        result_context.setdefault(
            "employee_full_name",
            employee.full_name,
        )

        # Если в модели User есть position можно получить название должности
        position = getattr(
            employee,
            "position",
            None,
        )

        if position is not None:
            result_context.setdefault(
                "employee_position",
                position.name,
            )
            result_context.setdefault(
                "position",
                position.name,
            )

        # Данные организации
        result_context.setdefault(
            "organization_name",
            settings.organization_name,
        )

        result_context.setdefault(
            "director_name",
            settings.director_name,
        )

        result_context.setdefault(
            "director_position",
            settings.director_position,
        )

        # Общая дата
        result_context.setdefault(
            "today",
            date.today().strftime(
                "%d.%m.%Y"
            ),
        )

        # Данные заявки
        result_context.setdefault(
            "request_id",
            request.id,
        )

        return result_context

    def _build_file_name(
        self,
        *,
        template_code: str,
        request_id: int,
    ) -> str:
        """
        Создаёт уникальное имя документа.

        Пример:

        vacation_application_request_15_a1b2c3d4.docx
        """

        unique_part = uuid.uuid4().hex[:8]

        return (
            f"{template_code}"
            f"_request_{request_id}"
            f"_{unique_part}.docx"
        )