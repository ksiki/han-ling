import uuid
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from fastapi.security import APIKeyCookie
from shared.exceptions import InvalidTokenException
from shared.security import verify_token

from src.core.settings import config
from src.db import UnitOfWork, async_session_maker
from src.models import UserORM


async def _get_uow() -> AsyncGenerator[UnitOfWork, None]:
    """Предоставляет асинхронный генератор с контекстом Unit of Work для внедрения зависимостей.

    Yields:
        UnitOfWork: Экземпляр Unit of Work в активном контексте транзакции.
    """
    uow = UnitOfWork(session_maker=async_session_maker)
    async with uow:
        yield uow


async def get_user_from_access_token(
    raw_token: Annotated[
        str, Depends(APIKeyCookie(name="access_token", auto_error=False))
    ],
    uow: Annotated[UnitOfWork, Depends(_get_uow)],
) -> UserORM:
    """Извлекает и проверяет пользователя на основе переданного access-токена из cookie.

    Args:
        raw_token: Необработанная строка токена доступа, извлеченная из cookie.
        uow: Экземпляр Unit of Work для доступа к базе данных.

    Returns:
        UserORM: Экземпляр найденного и подтвержденного пользователя.

    Raises:
        InvalidTokenException: Если токен невалиден, истек, имеет неверный тип или содержит некорректный ID, а также если пользователь не найден.
    """
    payload_dict = verify_token(
        token=raw_token,
        secret_key=config.SECRET_KEY,
        algorithm=config.ALGORITHM,
        expected_type="access",
    )
    user_id = payload_dict.get("sub", "")
    try:
        user = await uow.user.get_or_none(id=uuid.UUID(str(user_id)))
        if not user:
            raise InvalidTokenException
        return user
    except ValueError:
        raise InvalidTokenException
