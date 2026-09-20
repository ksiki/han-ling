from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def mock_uow() -> MagicMock:
    """Создает мок для UnitOfWork с замоканными репозиториями."""
    uow = MagicMock()
    uow.flush = AsyncMock()
    uow.commit = AsyncMock()
    uow.user.add = AsyncMock()
    uow.user.get = AsyncMock()
    uow.user.get_by_email = AsyncMock()
    uow.user_provider.add = AsyncMock()
    uow.user_provider.get_or_none = AsyncMock()
    uow.user_session.add = AsyncMock()
    uow.user_session.all_active_sessions = AsyncMock()
    uow.user_session.get_or_none = AsyncMock()
    return uow


@pytest.fixture
def mock_redis() -> AsyncMock:
    redis = AsyncMock()
    return redis
