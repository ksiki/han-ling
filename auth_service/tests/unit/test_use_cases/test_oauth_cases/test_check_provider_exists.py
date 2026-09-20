from unittest.mock import AsyncMock

from src.core.exceptions import ProviderLinkNotFoundException
from src.models import ProviderEnum


async def test_check_provider_exists_true(oauth_cases):
    oauth_cases._oauth_service.get_provider = AsyncMock(return_value=object())

    result = await oauth_cases._check_provider_exists(google_sub="google_123")

    assert result is True
    oauth_cases._oauth_service.get_provider.assert_called_once_with(
        provider_id="google_123", type=ProviderEnum.GOOGLE
    )


async def test_check_provider_exists_false(oauth_cases):
    oauth_cases._oauth_service.get_provider = AsyncMock(
        side_effect=ProviderLinkNotFoundException
    )

    result = await oauth_cases._check_provider_exists(google_sub="google_123")

    assert result is False
    oauth_cases._oauth_service.get_provider.assert_called_once_with(
        provider_id="google_123", type=ProviderEnum.GOOGLE
    )
