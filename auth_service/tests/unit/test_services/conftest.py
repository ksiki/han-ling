from unittest.mock import AsyncMock, MagicMock

import pytest

from src.services import (
    AuthService,
    OAuthService,
    OTPService,
    RecoveryService,
    RegistrationService,
    SessionService,
)


@pytest.fixture
def mock_uow() -> MagicMock:
    """Создает мок для UnitOfWork с замоканными репозиториями."""
    uow = MagicMock()
    uow.flush = AsyncMock()
    uow.user.add = AsyncMock()
    uow.user.get_by_email = AsyncMock()
    uow.user_provider.add = AsyncMock()
    uow.user_provider.get_or_none = AsyncMock()
    uow.user_session.add = AsyncMock()
    uow.user_session.all_active_sessions = AsyncMock()
    return uow


@pytest.fixture
def mock_redis() -> AsyncMock:
    redis = AsyncMock()
    return redis


@pytest.fixture
def auth_service(mock_uow) -> AuthService:
    return AuthService(uow=mock_uow)


@pytest.fixture
def oauth_service(mock_uow) -> OAuthService:
    return OAuthService(uow=mock_uow)


@pytest.fixture
def otp_service(mock_redis) -> OTPService:
    return OTPService(redis_client=mock_redis)


@pytest.fixture
def recovery_service(mock_uow) -> RecoveryService:
    return RecoveryService(uow=mock_uow)


@pytest.fixture
def registration_service(mock_uow) -> RegistrationService:
    return RegistrationService(uow=mock_uow)


@pytest.fixture
def session_service(mock_uow) -> SessionService:
    return SessionService(uow=mock_uow)
