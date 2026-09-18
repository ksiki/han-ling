import uuid
from collections.abc import AsyncGenerator, Awaitable, Callable, Coroutine
from typing import Annotated, Any

from fastapi import Depends, Request
from fastapi.security import APIKeyCookie
from redis.asyncio import Redis
from shared.exceptions import InvalidTokenException

from src.core.exceptions import UserBannedOrDeletedException
from src.core.security import verify_token
from src.db import UnitOfWork, async_session_maker
from src.models import UserORM
from src.redis.client import get_redis_client
from src.use_cases import (
    AuthCases,
    OAuthCases,
    PasswordResetCaces,
    ProfileCases,
    RegistrationCases,
    SessionCases,
)


async def _get_uow() -> AsyncGenerator[UnitOfWork, None]:
    """Предоставляет асинхронный генератор с контекстом Unit of Work для внедрения зависимостей.

    Yields:
        UnitOfWork: Экземпляр Unit of Work в активном контексте транзакции.
    """
    uow = UnitOfWork(session_maker=async_session_maker)
    async with uow:
        yield uow


def get_registration_cases(
    uow: UnitOfWork = Depends(_get_uow),
    redis_client: Redis = Depends(get_redis_client),
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
    redis_client: Redis = Depends(get_redis_client),
) -> PasswordResetCaces:
    """Создает и возвращает экземпляр сценариев восстановления доступа PasswordResetCaces.

    Args:
        uow: Экземпляр Unit of Work для управления транзакциями.
        redis_client: Асинхронный клиент Redis для работы с временными состояниями.

    Returns:
        PasswordResetCaces: Инициализированный сценарий Use Case для восстановления доступа.
    """
    return PasswordResetCaces(uow=uow, redis_client=redis_client)


def get_auth_cases(uow: UnitOfWork = Depends(_get_uow)) -> AuthCases:
    """Создает и возвращает экземпляр сценариев авторизации AuthCases.

    Args:
        uow: Экземпляр Unit of Work для управления транзакциями.

    Returns:
        AuthCases: Инициализированный сценарий Use Case для авторизации.
    """
    return AuthCases(uow=uow)


def get_oauth_cases(uow: UnitOfWork = Depends(_get_uow)) -> OAuthCases:
    """Создает и возвращает экземпляр сценариев авторизации через сторонние сервисы OAuthCases.

    Args:
        uow: Экземпляр Unit of Work для управления транзакциями.

    Returns:
        OAuthCases: Инициализированный сценарий Use Case для авторизации через сторонние сервисы.
    """
    return OAuthCases(uow=uow)


def get_session_cases(uow: UnitOfWork = Depends(_get_uow)) -> SessionCases:
    """Создает и возвращает экземпляр сценариев сессий SessionCases.

    Args:
        uow: Экземпляр Unit of Work для управления транзакциями.

    Returns:
        SessionCases: Инициализированный сценарий Use Case для сессий.
    """
    return SessionCases(uow=uow)


def get_profile_cases(uow: UnitOfWork = Depends(_get_uow)) -> ProfileCases:
    """Создает и возвращает экземпляр сценариев профиля ProfileCases.

    Args:
        uow: Экземпляр Unit of Work для управления транзакциями.

    Returns:
        ProfileCases: Инициализированный сценарий Use Case для профиля.
    """
    return ProfileCases(uow=uow)


def token_payload_verifier(
    token_getter: Callable[[Request], Awaitable[str | None]], expected_type: str
) -> Callable[[str], Coroutine[Any, Any, dict[str, Any]]]:
    """Создает фабрику зависимостей FastAPI для извлечения и верификации JWT-токена.

    Args:
        token_getter: Зависимость или схема безопасности для получения необработанной строки токена.
        expected_type: Ожидаемый тип токена (например, "access" или "refresh").

    Returns:
        Callable[[str], Coroutine[Any, Any, dict[str, Any]]]: Асинхронная функция-зависимость, возвращающая полезную нагрузку токена.
    """

    async def _verifier(
        raw_token: Annotated[str, Depends(token_getter)],
    ) -> dict[str, Any]:
        """Проверяет токен на валидность и совпадение типа, возвращая его полезную нагрузку.

        Args:
            raw_token: Необработанная строка токена, полученная из зависимости.

        Returns:
            dict[str, Any]: Расшифрованная полезная нагрузка токена.
        """
        payload_dict = verify_token(
            token=raw_token,
            expected_type=expected_type,
        )
        return payload_dict

    return _verifier


access_token_cookie_schema = APIKeyCookie(name="access_token", auto_error=False)
get_access_payload = token_payload_verifier(
    token_getter=access_token_cookie_schema,
    expected_type="access",
)

refresh_token_cookie_schema = APIKeyCookie(name="refresh_token", auto_error=False)
get_refresh_payload = token_payload_verifier(
    token_getter=refresh_token_cookie_schema,
    expected_type="refresh",
)


async def _get_active_user_by_id(
    user_id: uuid.UUID,
    uow: UnitOfWork,
) -> UserORM:
    """Получает пользователя по идентификатору и валидирует статус его учетной записи.

    Args:
        user_id: Идентификатор пользователя.
        uow: Экземпляр Unit of Work для доступа к репозиториям.

    Returns:
        UserORM: Экземпляр активного пользователя.

    Raises:
        InvalidTokenException: Если пользователь с данным ID не найден.
        UserBannedOrDeletedException: Если учетная запись неактивна или удалена.
    """
    user = await uow.user.get_or_none(id=user_id)
    if not user:
        raise InvalidTokenException
    if not user.is_valid:
        raise UserBannedOrDeletedException
    return user


def _safe_extract_uuid(payload: dict[str, Any], key: str) -> uuid.UUID:
    """Безопасно извлекает и валидирует UUID из полезной нагрузки токена по указанному ключу.

    Args:
        payload: Словарь данных полезной нагрузки JWT-токена.
        key: Ключ, по которому извлекается значение UUID.

    Returns:
        uuid.UUID: Преобразованный объект UUID.

    Raises:
        InvalidTokenException: Если значение отсутствует или имеет некорректный формат UUID.
    """
    raw_value = payload.get(key)
    try:
        return uuid.UUID(str(raw_value))
    except ValueError:
        raise InvalidTokenException


async def get_access_session_id(
    payload: Annotated[dict[str, Any], Depends(get_access_payload)],
) -> uuid.UUID:
    """Извлекает идентификатор сессии из полезной нагрузки access-токена.

    Args:
        payload: Полезная нагрузка проверенного access-токена.

    Returns:
        uuid.UUID: Идентификатор сессии пользователя.
    """
    return _safe_extract_uuid(payload=payload, key="session_id")


async def get_user_from_access_token(
    payload: Annotated[dict[str, Any], Depends(get_access_payload)],
    uow: Annotated[UnitOfWork, Depends(_get_uow)],
) -> UserORM:
    """Извлекает и валидирует активного пользователя на основе access-токена.

    Args:
        payload: Полезная нагрузка проверенного access-токена.
        uow: Экземпляр Unit of Work из зависимости FastAPI.

    Returns:
        UserORM: Экземпляр аутентифицированного активного пользователя.
    """
    return await _get_active_user_by_id(
        user_id=_safe_extract_uuid(payload=payload, key="sub"), uow=uow
    )


async def _check_refresh_session(uow: UnitOfWork, jti: uuid.UUID) -> None:
    """Проверяет существование и активность сессии по идентификатору jti токена.

    Args:
        uow: Экземпляр Unit of Work для доступа к сессиям в базе данных.
        jti: Уникальный идентификатор JWT токена (jti).

    Raises:
        InvalidTokenException: Если сессия не найдена или не является активной.
    """
    current_session = await uow.user_session.get_by_jti(jti=jti)
    if not current_session or not current_session.is_active:
        raise InvalidTokenException


async def get_user_from_refresh_token(
    payload: Annotated[dict[str, Any], Depends(get_refresh_payload)],
    uow: Annotated[UnitOfWork, Depends(_get_uow)],
) -> UserORM:
    """Извлекает и валидирует пользователя на основе refresh-токена с проверкой активности сессии.

    Args:
        payload: Полезная нагрузка проверенного refresh-токена.
        uow: Экземпляр Unit of Work из зависимости FastAPI.

    Returns:
        UserORM: Экземпляр аутентифицированного активного пользователя.

    Raises:
        InvalidTokenException: Если сессия по jti не найдена, отозвана или истекла.
    """
    await _check_refresh_session(
        uow=uow, jti=_safe_extract_uuid(payload=payload, key="jti")
    )
    return await _get_active_user_by_id(
        user_id=_safe_extract_uuid(payload=payload, key="sub"), uow=uow
    )


async def get_jti_from_refresh_token(
    payload: Annotated[dict[str, Any], Depends(get_refresh_payload)],
    uow: Annotated[UnitOfWork, Depends(_get_uow)],
) -> uuid.UUID:
    """Извлекает и верифицирует идентификатор jti активной сессии из refresh-токена.

    Args:
        payload: Полезная нагрузка проверенного refresh-токена.
        uow: Экземпляр Unit of Work из зависимости FastAPI.

    Returns:
        uuid.UUID: Валидный идентификатор jti сессии.

    Raises:
        InvalidTokenException: Если связанная сессия не найдена или неактивна.
    """
    jti = _safe_extract_uuid(payload=payload, key="jti")
    await _check_refresh_session(uow=uow, jti=jti)
    return jti
