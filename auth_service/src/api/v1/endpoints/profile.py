from fastapi import APIRouter, Depends, status

from src.api.dependencies import (
    get_profile_cases,
    get_user_from_access_token,
)
from src.models import UserORM
from src.schemas.common import SuccessResponse
from src.schemas.profile import ChangeNicknameRequest, ProfileResponse
from src.use_cases import ProfileCases

router = APIRouter(prefix="/profiles", tags=["Users v1"])


@router.get("/me", status_code=status.HTTP_200_OK, response_model=ProfileResponse)
async def get_me(
    user: UserORM = Depends(get_user_from_access_token),
) -> ProfileResponse:
    """Возвращает профиль текущего аутентифицированного пользователя.

    Args:
        user: Экземпляр текущего пользователя, полученный из access-токена.

    Returns:
        UserProfileResponse: DTO с данными профиля пользователя.
    """
    return ProfileResponse(
        id=user.id,
        email=user.email,
        nickname=user.nickname,
        role=user.role,
        registed_at=user.created_at,
    )


@router.patch(
    "/me/change-nickname",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponse,
)
async def change_nickname(
    payload: ChangeNicknameRequest,
    user: UserORM = Depends(get_user_from_access_token),
    profile_cases: ProfileCases = Depends(get_profile_cases),
) -> SuccessResponse:
    """Изменяет никнейм текущего аутентифицированного пользователя.

    Args:
        payload: Данные запроса, содержащие новый никнейм.
        user: Экземпляр текущего пользователя, извлеченный из access-токена.
        profile_cases: Сценарий (Use Case) управления профилем пользователя.

    Returns:
        SuccessResponse: Подтверждение успешного изменения никнейма.
    """
    await profile_cases.change_nickname(user_id=user.id, new_nickname=payload.nickname)
    return SuccessResponse()
