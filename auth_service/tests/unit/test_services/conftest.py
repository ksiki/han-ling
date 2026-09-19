from unittest.mock import AsyncMock, MagicMock

import pytest

from src.services import AuthService, OAuthService, OTPService


@pytest.fixture
def mock_uow() -> MagicMock:
    """Создает мок для UnitOfWork с замоканными репозиториями."""
    uow = MagicMock()
    uow.user.get_by_email = AsyncMock()
    uow.user_provider.add = AsyncMock()
    uow.user_provider.get_or_none = AsyncMock()
    uow.flush = AsyncMock()
    return uow


@pytest.fixture
def mock_redis():
    redis = AsyncMock()
    return redis


@pytest.fixture
def auth_service(mock_uow) -> AuthService:
    return AuthService(uow=mock_uow)


@pytest.fixture
def oauth_service(mock_uow):
    return OAuthService(uow=mock_uow)


@pytest.fixture
def otp_service(mock_redis):
    return OTPService(redis_client=mock_redis)
