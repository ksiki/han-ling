from unittest.mock import AsyncMock, MagicMock

from src.models import ProviderEnum


async def test_login_by_google_provider_exists(oauth_cases, mock_uow):
    """Тест: Провайдер уже привязан, создание новой связи пропускается, сессия успешно создается."""
    token_payload = {"email": "existing@example.com", "sub": "google_123"}
    oauth_cases._oauth_service.check_google_token = MagicMock(
        return_value=token_payload
    )
    oauth_cases._check_provider_exists = AsyncMock(return_value=True)

    mock_user = MagicMock()
    oauth_cases._get_or_create_user = AsyncMock(return_value=mock_user)
    oauth_cases._oauth_service.create_provider = AsyncMock()
    oauth_cases._session_service.create_session = AsyncMock(
        return_value=("access_token", "refresh_token")
    )

    result = await oauth_cases.login_by_google(
        id_token="valid_token", ip="127.0.0.1", user_agent="Mozilla/5.0"
    )

    assert result == ("access_token", "refresh_token")
    oauth_cases._oauth_service.check_google_token.assert_called_once_with(
        token="valid_token"
    )
    oauth_cases._check_provider_exists.assert_called_once_with("google_123")
    oauth_cases._get_or_create_user.assert_called_once_with("existing@example.com")
    oauth_cases._oauth_service.create_provider.assert_not_called()
    oauth_cases._session_service.create_session.assert_called_once_with(
        user=mock_user, ip="127.0.0.1", user_agent="Mozilla/5.0"
    )
    mock_uow.commit.assert_called_once()


async def test_login_by_google_provider_not_exists(oauth_cases, mock_uow):
    """Тест: Провайдер не привязан, выполняется создание новой связи перед выдачей сессии."""
    token_payload = {"email": "new@example.com", "sub": "google_456"}
    oauth_cases._oauth_service.check_google_token = MagicMock(
        return_value=token_payload
    )
    oauth_cases._check_provider_exists = AsyncMock(return_value=False)

    mock_user = MagicMock()
    mock_user.id = "user_uuid_123"
    oauth_cases._get_or_create_user = AsyncMock(return_value=mock_user)
    oauth_cases._oauth_service.create_provider = AsyncMock()
    oauth_cases._session_service.create_session = AsyncMock(
        return_value=("access_token", "refresh_token")
    )

    result = await oauth_cases.login_by_google(
        id_token="valid_token", ip="192.168.1.1", user_agent="Chrome"
    )

    assert result == ("access_token", "refresh_token")
    oauth_cases._oauth_service.create_provider.assert_called_once_with(
        user_id="user_uuid_123",
        provider_id="google_456",
        type=ProviderEnum.GOOGLE,
    )
    mock_uow.commit.assert_called_once()
