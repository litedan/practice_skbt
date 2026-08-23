"""
Сервис документов.

Подписание — заглушка под будущую интеграцию с ЭЦП/КЭП.
"""

from app.models.main.user import User
from app.schemas.document import DocumentSignResponse


class DocumentService:
    async def sign_document(self, *, current_user: User, document_id: int) -> DocumentSignResponse:
        # TODO: проверка существования документа, прав доступа, вызов провайдера ЭЦП
        return DocumentSignResponse(
            document_id=document_id,
            status="stub",
            message=(
                "Подписание документов пока не реализовано. "
                "Планируется интеграция с ЭЦП/КЭП и запись факта подписи в БД."
            ),
            signed_at=None,
        )
