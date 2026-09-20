import pytest

from src.use_cases import (
    AuthCases,
    OAuthCases,
    PasswordResetCaces,
    ProfileCases,
    RegistrationCases,
    SessionCases,
)


@pytest.fixture
def auth_cases(mock_uow) -> AuthCases:
    return AuthCases(uow=mock_uow)


@pytest.fixture
def oauth_cases(mock_uow):
    return OAuthCases(uow=mock_uow)


@pytest.fixture
def password_reset_cases(mock_uow, mock_redis):
    return PasswordResetCaces(uow=mock_uow, redis_client=mock_redis)


@pytest.fixture
def profile_cases(mock_uow):
    return ProfileCases(uow=mock_uow)


@pytest.fixture
def registration_cases(mock_uow, mock_redis):
    return RegistrationCases(uow=mock_uow, redis_client=mock_redis)


@pytest.fixture
def session_cases(mock_uow):
    return SessionCases(uow=mock_uow)
