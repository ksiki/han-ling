from fastapi import Response

from src.core.settings import config

_SECURE_FLAG: bool = not config.DEBUG
_DEFAULT_PATH: str = "/"
_DEFAULT_SAMESITE: str = "lax"


def refresh_access_cookies(
    response: Response,
    access_token: str,
) -> None:
    """Устанавливает или обновляет cookie с access-токеном в HTTP-ответе.

    Args:
        response: Объект ответа FastAPI для записи cookie.
        access_token: Строка с новым access-токеном.
    """
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=_SECURE_FLAG,
        samesite=_DEFAULT_SAMESITE,
        path=_DEFAULT_PATH,
        max_age=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


def set_auth_cookies(
    response: Response,
    *,
    access_token: str,
    refresh_token: str,
) -> None:
    """Устанавливает авторизационные cookie с access- и refresh-токенами в HTTP-ответе.

    Args:
        response: Объект ответа FastAPI для записи cookie.
        access_token: Строка с access-токеном пользователя.
        refresh_token: Строка с refresh-токеном пользователя.
    """
    refresh_access_cookies(response=response, access_token=access_token)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=_SECURE_FLAG,
        samesite=_DEFAULT_SAMESITE,
        path=_DEFAULT_PATH,
        max_age=config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )


def clear_auth_cookies(response: Response) -> None:
    """Удаляет авторизационные cookie (access- и refresh-токены) из HTTP-ответа.

    Args:
        response: Объект ответа FastAPI для удаления cookie.
    """
    for key in ("access_token", "refresh_token"):
        response.delete_cookie(
            key=key,
            path=_DEFAULT_PATH,
            httponly=True,
            secure=_SECURE_FLAG,
            samesite=_DEFAULT_SAMESITE,
        )
