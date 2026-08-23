"""Авторизация: login / refresh."""

from fastapi import APIRouter, status

from app.api.deps import AuthServiceDep, ClientInfoDep
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    payload: LoginRequest,
    auth_service: AuthServiceDep,
    client: ClientInfoDep,
) -> TokenResponse:
    """Аутентификация по email/password. Запись в auth_log."""
    return await auth_service.login(
        payload,
        ip_address=client.ip_address,
        user_agent=client.user_agent,
    )


@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh_token(
    payload: RefreshRequest,
    auth_service: AuthServiceDep,
) -> TokenResponse:
    """Обновление пары access/refresh токенов."""
    return await auth_service.refresh(payload.refresh_token)
