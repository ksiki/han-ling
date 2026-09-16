import uuid

from fastapi import APIRouter, Depends, status

from src.api.dependencies import (
    get_access_session_id,
    get_session_cases,
    get_user_from_access_token,
)
from src.models import UserORM
from src.schemas.users import SessionsListResponse, UserProfileResponse
from src.use_cases import SessionCases

router = APIRouter(prefix="/users", tags=["Users v1"])


@router.get("/me", status_code=status.HTTP_200_OK, response_model=UserProfileResponse)
async def get_me(
    user: UserORM = Depends(get_user_from_access_token),
) -> UserProfileResponse:
    """Возвращает профиль текущего аутентифицированного пользователя.

    Args:
        user: Экземпляр текущего пользователя, полученный из access-токена.

    Returns:
        UserProfileResponse: DTO с данными профиля пользователя.
    """
    return UserProfileResponse(
        id=user.id, email=user.email, role=user.role, registed_at=user.created_at
    )


@router.get(
    "/me/sessions", status_code=status.HTTP_200_OK, response_model=SessionsListResponse
)
async def get_active_sessions(
    current_session_id: uuid.UUID = Depends(get_access_session_id),
    user: UserORM = Depends(get_user_from_access_token),
    session_cases: SessionCases = Depends(get_session_cases),
) -> SessionsListResponse:
    """Возвращает список всех активных сессий текущего пользователя.

    Args:
        current_session_id: Идентификатор текущей активной сессии из токена доступа.
        user: Экземпляр аутентифицированного пользователя.
        session_cases: Сценарий (Use Case) управления сессиями.

    Returns:
        SessionsListResponse: Список активных сессий с отметкой текущей.
    """
    sessions = await session_cases.all_active_sessions(
        currents_session_id=current_session_id, user_id=user.id
    )
    return SessionsListResponse(sessions=sessions)
