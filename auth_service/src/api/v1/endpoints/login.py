from typing import Annotated, Any

from fastapi import APIRouter, Depends, Response, status

from src.api.dependencies import (
    get_login_service,
    refresh_token_cookie_schema,
    verify_access_token,
    verify_refresh_token,
)
from src.core.settings import config
from src.models.user import UserORM
from src.schemas.login import UserLoginRequest
from src.services import LoginService

router = APIRouter(tags=["Login v1"])


@router.post(
    "/",
    status_code=status.HTTP_200_OK,
)
async def login(
    payload: UserLoginRequest,
    response: Response,
    login_service: LoginService = Depends(get_login_service),
) -> dict[str, Any]:
    """
    Вход для пользователя

    Принимает:
        - payload для входа

    Исключения:
        - если пользователя с таким email не существует: 401 Unauthorized
        - если пароли неверный: 401 Unauthorized
    """

    access_token, refresh_token = await login_service.login_user(
        email=payload.email,
        password=payload.password,
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=not config.DEBUG,
        samesite="lax",
        max_age=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=not config.DEBUG,
        samesite="lax",
        max_age=config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return {"ok": True}


@router.post(
    "/out",
    status_code=status.HTTP_200_OK,
)
async def logout(
    refresh_token: Annotated[str, Depends(refresh_token_cookie_schema)],
    response: Response,
    user_orm: UserORM = Depends(verify_access_token),
    login_service: LoginService = Depends(get_login_service),
) -> dict[str, Any]:
    """
    Выход из аккаунта и внесение refresh токена в блэклист
    """
    await login_service.logout_user(refresh_token=refresh_token)

    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=not config.DEBUG,
        samesite="lax",
    )
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=not config.DEBUG,
        samesite="lax",
    )

    return {"ok": True}


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
)
async def refresh_access_token(
    response: Response,
    user_orm: UserORM = Depends(verify_refresh_token),
    login_service: LoginService = Depends(get_login_service),
) -> dict[str, Any]:
    access_token = await login_service.refresh_access_token(user=user_orm)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=not config.DEBUG,
        samesite="lax",
        max_age=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return {"ok": True}
