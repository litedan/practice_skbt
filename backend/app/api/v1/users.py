"""
Эндпоинты пользователей.

Пример работы с изолированными ПД: GET/PUT /users/{id}/private-data
"""

from fastapi import APIRouter

from app.api.deps import ClientInfoDep, CurrentUser, PrivateDataServiceDep, UserServiceDep
from app.core.exceptions import ForbiddenError
from app.core.rbac import can_read_user_profile
from app.schemas.user import UserMeRead, UserRead
from app.schemas.user_private_data import UserPrivateDataRead, UserPrivateDataUpdate
from app.services.user_presenter import build_user_me_read, build_user_read

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserMeRead)
async def get_current_user_profile(current_user: CurrentUser) -> UserMeRead:
    """Профиль текущего авторизованного пользователя с ролью и permissions."""
    return build_user_me_read(current_user)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    current_user: CurrentUser,
    user_service: UserServiceDep,
) -> UserRead:
    """Профиль: свой / HR и admin — любой / руководитель — сотрудники своего отдела."""
    user = await user_service.get_by_id(user_id)
    if not can_read_user_profile(current_user, user):
        raise ForbiddenError("Нет прав на просмотр профиля пользователя")
    return build_user_read(user)


@router.get("/{user_id}/private-data", response_model=UserPrivateDataRead)
async def get_user_private_data(
    user_id: int,
    current_user: CurrentUser,
    service: PrivateDataServiceDep,
    client: ClientInfoDep,
) -> UserPrivateDataRead:
    """
    Получение персональных данных.

    Доступ: владелец или HR. Каждый запрос логируется в sensitive_acces_log.
    """
    return await service.get_private_data(
        target_user_id=user_id,
        current_user=current_user,
        ip_address=client.ip_address,
        user_agent=client.user_agent,
    )


@router.put("/{user_id}/private-data", response_model=UserPrivateDataRead)
async def update_user_private_data(
    user_id: int,
    payload: UserPrivateDataUpdate,
    current_user: CurrentUser,
    service: PrivateDataServiceDep,
    client: ClientInfoDep,
) -> UserPrivateDataRead:
    """
    Обновление персональных данных.

    Доступ: владелец или HR. Изменения логируются в sensitive_acces_log.
    """
    return await service.update_private_data(
        target_user_id=user_id,
        current_user=current_user,
        payload=payload,
        ip_address=client.ip_address,
        user_agent=client.user_agent,
    )
