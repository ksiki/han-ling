from collections.abc import AsyncGenerator
from typing import Annotated, Any

from fastapi import Depends
from fastapi.security import APIKeyCookie
from redis.asyncio import Redis
from shared.exceptions import InvalidTokenException

from src.core.exceptions import UserBannedOrDeletedException
from src.core.security import verify_token
from src.db import UnitOfWork, async_session_maker
from src.models import UserORM
from src.redis.client import get_redis_client
from src.use_cases import PasswordResetCaces, RegistrationCases

access_token_cookie_schema = APIKeyCookie(name="access_token", auto_error=False)
refresh_token_cookie_schema = APIKeyCookie(name="refresh_token", auto_error=False)


async def _get_uow() -> AsyncGenerator[UnitOfWork, None]:
    """Предоставляет асинхронный генератор с контекстом Unit of Work для внедрения зависимостей.

    Yields:
        UnitOfWork: Экземпляр Unit of Work в активном контексте транзакции.
    """
    uow = UnitOfWork(session_maker=async_session_maker)
    async with uow:
        yield uow


async def _get_redis_client() -> Redis:
    """Возвращает экземпляр асинхронного клиента Redis для внедрения зависимостей.

    Returns:
        Redis: Экземпляр клиента Redis.
    """
    return get_redis_client()


async def _get_user_by_token_payload(
    payload: dict[str, Any],
    uow: UnitOfWork = Depends(_get_uow),
) -> UserORM | None:
    """Извлекает пользователя по полезной нагрузке JWT-токена и валидирует его статус.

    Args:
        payload: Данные полезной нагрузки JWT-токена, содержащие sub (ID пользователя).
        uow: Экземпляр Unit of Work для доступа к базе данных.

    Returns:
        UserORM | None: Экземпляр активного пользователя.

    Raises:
        InvalidTokenException: Если пользователь с данным ID не найден в базе данных.
        UserBannedOrDeletedException: Если пользователь деактивирован, заблокирован или помечен удаленным.
    """
    user_id = payload.get("sub")
    user = await uow.user.get_or_none(id=user_id)

    if not user:
        raise InvalidTokenException
    if not user.is_valid:
        raise UserBannedOrDeletedException

    return user


def get_registration_cases(
    uow: UnitOfWork = Depends(_get_uow),
    redis_client: Redis = Depends(_get_redis_client),
) -> RegistrationCases:
    """Создает и возвращает экземпляр сценариев регистрации RegistrationCases.

    Args:
        uow: Экземпляр Unit of Work для управления транзакциями.
        redis_client: Асинхронный клиент Redis для работы с временными состояниями.

    Returns:
        RegistrationCases: Инициализированный сценарий Use Case для регистрации.
    """
    return RegistrationCases(uow=uow, redis_client=redis_client)


def get_password_recovery_cases(
    uow: UnitOfWork = Depends(_get_uow),
    redis_client: Redis = Depends(_get_redis_client),
) -> PasswordResetCaces:
    """Создает и возвращает экземпляр сценариев восстановления доступа PasswordResetCaces.

    Args:
        uow: Экземпляр Unit of Work для управления транзакциями.
        redis_client: Асинхронный клиент Redis для работы с временными состояниями.

    Returns:
        PasswordResetCaces: Инициализированный сценарий Use Case для восстановления доступа.
    """
    return PasswordResetCaces(uow=uow, redis_client=redis_client)


async def verify_access_token(
    access_token: Annotated[str, Depends(access_token_cookie_schema)],
    uow: UnitOfWork = Depends(_get_uow),
) -> UserORM:
    decode_payload = verify_token(
        token=access_token,
        expected_type="access",
    )

    return await _get_user_by_token_payload(payload=decode_payload, uow=uow)


async def verify_refresh_token(
    refresh_token: Annotated[str, Depends(refresh_token_cookie_schema)],
    uow: UnitOfWork = Depends(_get_uow),
) -> UserORM:
    decode_payload = verify_token(
        token=refresh_token,
        expected_type="refresh",
    )

    current_session = await uow.user_sesson.get_or_none_by_jti(
        jti=decode_payload.get("jti")
    )
    if not current_session or current_session.is_revoked:
        raise InvalidTokenException

    return await _get_user_by_token_payload(payload=decode_payload)
