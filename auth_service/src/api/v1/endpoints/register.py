from typing import Any

from fastapi import APIRouter, Depends, Response, status

from src.api.dependencies import get_register_service
from src.core.settings import config
from src.schemas.register import UserRegisterRequest
from src.services.register import RegisterService

router = APIRouter(tags=["Register v1"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
async def register(
    payload: UserRegisterRequest,
    response: Response,
    register_service: RegisterService = Depends(get_register_service),
) -> dict[str, Any]:
    """
    Регистрация нового пользователя

    Принимает:
        - payload для регистрации

    Исключения:
        - если пароль и повтор пароля не совпадают: 400 Bad Request
        - если пользователь с такой почтой уже существует: 409 Conflict
    """

    access_token, refresh_token = await register_service.register(
        email=payload.email,
        password=payload.password,
        password_replay=payload.password_replay,
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
