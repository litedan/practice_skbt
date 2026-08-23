"""Кадровые заявки: CRUD, файлы, HR-статистика."""

from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from fastapi.responses import FileResponse

from app.api.deps import ClientInfoDep, CurrentUser, RequestServiceDep, require_permission
from app.core.permissions import Permission
from app.models.main.user import User
from app.schemas.request import (
    DocumentFileRead,
    RequestCreate,
    RequestDetailRead,
    RequestRead,
    RequestStatsRead,
    RequestUpdate,
)

router = APIRouter(prefix="/requests", tags=["Requests"])


@router.get("/stats", response_model=RequestStatsRead)
async def get_request_stats(
    current_user: CurrentUser,
    service: RequestServiceDep,
) -> RequestStatsRead:
    """HR-панель: агрегированная статистика по статусам."""
    return await service.get_hr_stats(current_user=current_user)


@router.get("", response_model=list[RequestRead])
async def list_requests(
    current_user: CurrentUser,
    service: RequestServiceDep,
    status_id: int | None = Query(default=None),
    request_type_id: int | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[RequestRead]:
    """Список заявок: сотрудник — свои; HR — все (с фильтрами)."""
    return await service.list_requests(
        current_user=current_user,
        status_id=status_id,
        request_type_id=request_type_id,
        skip=skip,
        limit=limit,
    )


@router.get("/{request_id}", response_model=RequestDetailRead)
async def get_request(
    request_id: int,
    current_user: CurrentUser,
    service: RequestServiceDep,
) -> RequestDetailRead:
    """Детали заявки с вложениями."""
    return await service.get_request(current_user=current_user, request_id=request_id)


@router.post("", response_model=RequestRead, status_code=status.HTTP_201_CREATED)
async def create_request(
    payload: RequestCreate,
    current_user: Annotated[User, Depends(require_permission(Permission.REQUESTS_CREATE))],
    service: RequestServiceDep,
    client: ClientInfoDep,
) -> RequestRead:
    """Создание новой кадровой заявки (статус «Новая»)."""
    return await service.create_request(
        current_user=current_user,
        payload=payload,
        ip_address=client.ip_address,
        user_agent=client.user_agent,
    )


@router.patch("/{request_id}", response_model=RequestRead)
async def update_request(
    request_id: int,
    payload: RequestUpdate,
    current_user: CurrentUser,
    service: RequestServiceDep,
    client: ClientInfoDep,
) -> RequestRead:
    """Обновление заявки: HR — статус/checker; сотрудник — comment (только «Новая»)."""
    return await service.update_request(
        current_user=current_user,
        request_id=request_id,
        payload=payload,
        ip_address=client.ip_address,
        user_agent=client.user_agent,
    )


@router.post(
    "/{request_id}/files",
    response_model=DocumentFileRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_request_file(
    request_id: int,
    current_user: Annotated[User, Depends(require_permission(Permission.REQUESTS_CREATE))],
    service: RequestServiceDep,
    file: UploadFile = File(...),
) -> DocumentFileRead:
    """Загрузка файла к заявке (только автор)."""
    content = await file.read()
    filename = file.filename or "upload"
    return await service.upload_file(
        current_user=current_user,
        request_id=request_id,
        filename=filename,
        content=content,
    )


@router.get("/{request_id}/files", response_model=list[DocumentFileRead])
async def list_request_files(
    request_id: int,
    current_user: CurrentUser,
    service: RequestServiceDep,
) -> list[DocumentFileRead]:
    """Список файлов, прикреплённых к заявке."""
    return await service.list_files(current_user=current_user, request_id=request_id)


@router.get("/{request_id}/files/{file_id}")
async def download_request_file(
    request_id: int,
    file_id: int,
    current_user: CurrentUser,
    service: RequestServiceDep,
) -> FileResponse:
    """Скачивание файла заявки."""
    doc, path = await service.get_file_for_download(
        current_user=current_user,
        request_id=request_id,
        file_id=file_id,
    )
    return FileResponse(
        path=path,
        filename=doc.name,
        media_type="application/octet-stream",
    )
