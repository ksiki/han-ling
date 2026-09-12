from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from fastapi.security import APIKeyCookie
from redis.asyncio import Redis
from shared.exceptions import InvalidTokenException
from shared.security import verify_token

from src.core.settings import config
from src.db import UnitOfWork, async_session_maker
from src.models import UserORM
from src.redis import TokenBlacklistService
from src.redis.client import get_redis_client
from src.services import LoginService, RegisterService

access_token_cookie_schema = APIKeyCookie(name="access_token", auto_error=False)
refresh_token_cookie_schema = APIKeyCookie(name="refresh_token", auto_error=False)


async def _get_uow() -> AsyncGenerator[UnitOfWork, None]:
    uow = UnitOfWork(session_maker=async_session_maker)
    async with uow:
        yield uow


def _get_token_blacklist_service(
    redis_client: Redis = Depends(get_redis_client),
) -> TokenBlacklistService:
    return TokenBlacklistService(redis_client=redis_client)


def get_register_service(uow: UnitOfWork = Depends(_get_uow)) -> RegisterService:
    return RegisterService(uow=uow)


def get_login_service(
    uow: UnitOfWork = Depends(_get_uow),
    token_blacklist_service: TokenBlacklistService = Depends(
        _get_token_blacklist_service
    ),
) -> LoginService:
    return LoginService(uow=uow, token_blacklist=token_blacklist_service)


async def verify_access_token(
    access_token: Annotated[str, Depends(access_token_cookie_schema)],
    uow: UnitOfWork = Depends(_get_uow),
) -> UserORM:
    decode_payload = verify_token(
        token=access_token,
        secret_key=config.SECRET_KEY,
        algorithm=config.ALGORITHM,
        expected_type="access",
    )

    user = await uow.user.get_by_token_payload(payload=decode_payload)
    if not user:
        raise InvalidTokenException
    return user


async def verify_refresh_token(
    refresh_token: Annotated[str, Depends(refresh_token_cookie_schema)],
    uow: UnitOfWork = Depends(_get_uow),
    token_blacklist_service: TokenBlacklistService = Depends(
        _get_token_blacklist_service
    ),
) -> UserORM:
    decode_payload = verify_token(
        token=refresh_token,
        secret_key=config.SECRET_KEY,
        algorithm=config.ALGORITHM,
        expected_type="refresh",
    )

    is_blacklist = await token_blacklist_service.is_blacklist(
        jti=decode_payload.get("jti")
    )
    if is_blacklist:
        raise InvalidTokenException

    user = await uow.user.get_by_token_payload(payload=decode_payload)
    if not user:
        raise InvalidTokenException
    return user
