import uuid

from fastapi import APIRouter, Depends, Request, Response, status

from src.api.cookies import clear_auth_cookies, refresh_access_cookies, set_auth_cookies
from src.api.dependencies import (
    get_access_session_id,
    get_auth_cases,
    get_jti_from_refresh_token,
    get_session_cases,
    get_user_from_access_token,
    get_user_from_refresh_token,
)
from src.models import UserORM
from src.schemas.common import SuccessResponse
from src.schemas.login import LoginRequest
from src.use_cases import AuthCases, SessionCases

router = APIRouter(tags=["Auth v1"])


@router.post("/login", status_code=status.HTTP_200_OK, response_model=SuccessResponse)
async def login_by_email(
    payload: LoginRequest,
    request: Request,
    response: Response,
    auth_cases: AuthCases = Depends(get_auth_cases),
) -> SuccessResponse:
    """Аутентифицирует пользователя по email и паролю и устанавливает auth-cookie.

    Args:
        payload: Данные учетной записи (email, пароль, токен капчи).
        request: Объект текущего HTTP-запроса для извлечения сетевых данных клиента (IP, User-Agent).
        response: Объект HTTP-ответа для записи авторизационных токенов в cookie.
        auth_cases: Сценарий (Use Case) аутентификации пользователя.

    Returns:
        SuccessResponse: Подтверждение успешного входа в систему.
    """
    ip = request.headers.get(
        "X-Forwarded-For", request.client.host if request.client else "Unknown"
    )
    user_agent = request.headers.get("User-Agent", "Unknown")

    access_token, refresh_token = await auth_cases.login_by_email(
        captcha_token=payload.captcha_token,
        email=payload.email,
        password=payload.password,
        ip=ip,
        user_agent=user_agent,
    )
    set_auth_cookies(
        response=response, access_token=access_token, refresh_token=refresh_token
    )

    return SuccessResponse()


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponse,
)
async def refresh_access_token(
    response: Response,
    user: UserORM = Depends(get_user_from_refresh_token),
    refresh_jti: uuid.UUID = Depends(get_jti_from_refresh_token),
    auth_cases: AuthCases = Depends(get_auth_cases),
) -> SuccessResponse:
    """Обновляет истекший access-токен по действующему refresh-токену.

    Args:
        response: Объект HTTP-ответа для обновления access-cookie.
        user: Экземпляр пользователя, полученный из валидного refresh-токена.
        auth_cases: Сценарий (Use Case) аутентификации.

    Returns:
        SuccessResponse: Подтверждение успешного обновления токена.
    """
    access_token = await auth_cases.update_access_token(
        user_id=user.id, user_role=user.role.value, refresh_jti=refresh_jti
    )
    refresh_access_cookies(response=response, access_token=access_token)
    return SuccessResponse()


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponse,
)
async def logout(
    response: Response,
    session_id: uuid.UUID = Depends(get_access_session_id),
    session_cases: SessionCases = Depends(get_session_cases),
) -> SuccessResponse:
    """Завершает текущую сессию пользователя и удаляет авторизационные cookie.

    Args:
        response: Объект HTTP-ответа для удаления cookie.
        session_id: Идентификатор текущей сессии, извлеченный из access-токена.
        session_cases: Сценарий (Use Case) управления сессиями.

    Returns:
        SuccessResponse: Подтверждение успешного выхода из системы.
    """
    await session_cases.revoke_session_by_id(session_id=session_id)
    clear_auth_cookies(response=response)
    return SuccessResponse()


@router.delete(
    "/session/{session_id}",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponse,
)
async def revoke_session(
    session_id: uuid.UUID,
    user: UserORM = Depends(get_user_from_access_token),
    session_cases: SessionCases = Depends(get_session_cases),
) -> SuccessResponse:
    """Отзывает конкретную сессию пользователя по ее идентификатору.

    Args:
        session_id: Идентификатор отзываемой сессии.
        user: Экземпляр текущего аутентифицированного пользователя.
        session_cases: Сценарий (Use Case) управления сессиями.

    Returns:
        SuccessResponse: Подтверждение успешного отзыва сессии.
    """
    await session_cases.revoke_session_by_id(session_id=session_id, user_id=user.id)
    return SuccessResponse()
