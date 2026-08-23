"""Документы сотрудника (экран «Документы» в ЛК)."""

from fastapi import APIRouter, status

from app.api.deps import CurrentUser, DocumentServiceDep
from app.schemas.document import DocumentSignResponse

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post(
    "/{document_id}/sign",
    response_model=DocumentSignResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def sign_document(
    document_id: int,
    current_user: CurrentUser,
    service: DocumentServiceDep,
) -> DocumentSignResponse:
    """
    Заглушка подписания документа.

    В production здесь будет:
    - проверка, что документ принадлежит пользователю;
    - вызов криптопровайдера (ЭЦП/КЭП);
    - сохранение подписи и timestamp в БД + audit_log.
    """
    return await service.sign_document(current_user=current_user, document_id=document_id)
