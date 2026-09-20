from unittest.mock import AsyncMock, MagicMock

from src.core.exceptions import PasswordOrEmailInvalidException


async def test_get_or_create_user_existing_user(oauth_cases):
    mock_user = MagicMock()
    oauth_cases._auth_service.authenticate = AsyncMock(return_value=mock_user)
    oauth_cases._registration_service.create_user = AsyncMock()

    result = await oauth_cases._get_or_create_user(email="existing@example.com")

    assert result == mock_user
    oauth_cases._auth_service.authenticate.assert_called_once_with(
        email="existing@example.com", password=None
    )
    oauth_cases._registration_service.create_user.assert_not_called()


async def test_get_or_create_user_new_user(oauth_cases):
    mock_new_user = MagicMock()
    oauth_cases._auth_service.authenticate = AsyncMock(
        side_effect=PasswordOrEmailInvalidException
    )
    oauth_cases._registration_service.create_user = AsyncMock(
        return_value=mock_new_user
    )

    result = await oauth_cases._get_or_create_user(email="new@example.com")

    assert result == mock_new_user
    oauth_cases._auth_service.authenticate.assert_called_once_with(
        email="new@example.com", password=None
    )
    oauth_cases._registration_service.create_user.assert_called_once_with(
        email="new@example.com", password_hash=None
    )
