from unittest.mock import AsyncMock, MagicMock

import pytest

from src.services import AuthService, OAuthService


@pytest.fixture
def mock_uow() -> MagicMock:
    """Создает мок для UnitOfWork с замоканными репозиториями."""
    uow = MagicMock()
    uow.user.get_by_email = AsyncMock()
    return uow


@pytest.fixture
def auth_service(mock_uow) -> AuthService:
    return AuthService(uow=mock_uow)


@pytest.fixture
def oauth_service(mock_uow):
    """Инициализирует OAuthService с замоканным UnitOfWork."""
    return OAuthService(uow=mock_uow)
