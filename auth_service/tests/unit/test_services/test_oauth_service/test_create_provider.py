import uuid
from unittest.mock import MagicMock

import pytest

from src.models import UserProviderORM


async def test_create_provider_success(oauth_service, mock_uow):
    """Тест: Успешное создание провайдера и добавление в uow."""
    user_id = uuid.uuid4()
    provider_id = "google_123456789"
    provider_type = MagicMock()

    result = await oauth_service.create_provider(
        user_id=user_id, provider_id=provider_id, type=provider_type
    )

    assert isinstance(result, UserProviderORM)
    assert result.user_id == user_id
    assert result.provider_id == provider_id
    assert result.provider == provider_type

    mock_uow.user_provider.add.assert_called_once_with(result)
    mock_uow.flush.assert_called_once()


async def test_create_provider_db_error(oauth_service, mock_uow):
    """Тест: Провал при ошибке на уровне UnitOfWork (например, IntegrityError)."""
    user_id = uuid.uuid4()

    mock_error = Exception("Database Integrity Error")
    mock_uow.user_provider.add.side_effect = mock_error

    with pytest.raises(Exception) as exc_info:
        await oauth_service.create_provider(
            user_id=user_id, provider_id="some_id", type=MagicMock()
        )

    assert str(exc_info.value) == "Database Integrity Error"

    mock_uow.user_provider.add.assert_called_once()
    mock_uow.flush.assert_not_called()
