"""Документы сотрудника (экран «Документы» в ЛК)."""

from fastapi import APIRouter, status

from app.api.deps import CurrentUser, DocumentServiceDep
from app.schemas.document import DocumentSignRequest, DocumentSignResponse

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post(
    "/{document_id}/sign",
    response_model=DocumentSignResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def sign_document(
    document_id: int,
    payload: DocumentSignRequest,
    current_user: CurrentUser,
    service: DocumentServiceDep,
) -> DocumentSignResponse:
    return await service.sign_document(
        current_user=current_user,
        document_id=document_id,
        password=payload.password,
    )
