from unittest.mock import MagicMock

import pytest

from src.core.exceptions import ProviderLinkNotFoundException
from src.models import UserProviderORM


async def test_get_provider_success(oauth_service, mock_uow):
    """Тест: Успешное получение привязки провайдера."""
    provider_id = "google_123456789"
    provider_type = MagicMock()

    mock_provider_link = MagicMock(spec=UserProviderORM)
    mock_uow.user_provider.get_or_none.return_value = mock_provider_link

    result = await oauth_service.get_provider(
        provider_id=provider_id, type=provider_type
    )

    assert result == mock_provider_link
    mock_uow.user_provider.get_or_none.assert_called_once_with(
        provider_id=provider_id, provider=provider_type
    )


async def test_get_provider_not_found(oauth_service, mock_uow):
    """Тест: Ошибка ProviderLinkNotFoundException, если привязка не найдена."""
    provider_id = "unknown_google_id"
    provider_type = MagicMock()

    mock_uow.user_provider.get_or_none.return_value = None

    with pytest.raises(ProviderLinkNotFoundException):
        await oauth_service.get_provider(provider_id=provider_id, type=provider_type)

    mock_uow.user_provider.get_or_none.assert_called_once_with(
        provider_id=provider_id, provider=provider_type
    )
