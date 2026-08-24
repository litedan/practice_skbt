"""Авторизация: login / refresh / logout."""

from fastapi import APIRouter, status

from app.api.deps import AuthServiceDep, ClientInfoDep, CurrentUser
from app.schemas.auth import LoginRequest, LogoutRequest, RefreshRequest, TokenResponse
from app.schemas.common import MessageResponse

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
    """Ротация пары access/refresh. Старый refresh отзывается."""
    return await auth_service.refresh(payload.refresh_token)


@router.post("/logout", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def logout(
    payload: LogoutRequest,
    current_user: CurrentUser,
    auth_service: AuthServiceDep,
    client: ClientInfoDep,
) -> MessageResponse:
    """
    Выход из системы.

    Передайте `refresh_token`, чтобы отозвать текущую сессию,
    или `all_sessions=true`, чтобы отозвать все refresh-токены пользователя.
    Access-токен перестанет приниматься после истечения TTL.
    """
    await auth_service.logout(
        user=current_user,
        refresh_token=payload.refresh_token,
        all_sessions=payload.all_sessions,
        ip_address=client.ip_address,
        user_agent=client.user_agent,
    )
    return MessageResponse(detail="Выход выполнен")
