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
