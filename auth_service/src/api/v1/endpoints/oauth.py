from fastapi import APIRouter, Depends, Request, Response, status

from src.api.cookies import set_auth_cookies
from src.api.dependencies import get_oauth_cases
from src.schemas.common import SuccessResponse
from src.schemas.login import GoogleLoginRequest
from src.use_cases import OAuthCases

router = APIRouter(tags=["OAuth v1"])


@router.post(
    "/google/login", status_code=status.HTTP_200_OK, response_model=SuccessResponse
)
async def login_by_google(
    payload: GoogleLoginRequest,
    request: Request,
    response: Response,
    oauth_cases: OAuthCases = Depends(get_oauth_cases),
) -> SuccessResponse:
    """Выполняет вход через Google OAuth, создавая сессию и устанавливая auth-cookie.

    Args:
        payload: Данные запроса, содержащие Google ID Token.
        request: Объект текущего HTTP-запроса для извлечения сетевых метаданных клиента (IP, User-Agent).
        response: Объект HTTP-ответа для записи авторизационных токенов в cookie.
        oauth_cases: Сценарий (Use Case) управления OAuth-аутентификацией.

    Returns:
        SuccessResponse: Подтверждение успешной аутентификации и входа в систему.
    """
    ip = request.headers.get(
        "X-Forwarded-For", request.client.host if request.client else "Unknown"
    )
    user_agent = request.headers.get("User-Agent", "Unknown")

    access_token, refresh_token = await oauth_cases.login_by_google(
        id_token=payload.id_token,
        ip=ip,
        user_agent=user_agent,
    )
    set_auth_cookies(
        response=response, access_token=access_token, refresh_token=refresh_token
    )
    return SuccessResponse()
