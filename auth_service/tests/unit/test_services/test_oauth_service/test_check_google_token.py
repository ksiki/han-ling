import pytest

# Замени пути на реальные
from src.core.exceptions import GoogleTokenInvalidException


def test_check_google_token_success(oauth_service, mocker):
    """Тест: Успешная верификация токена, возвращается полезная нагрузка."""
    token = "valid_google_token"
    expected_payload = {
        "email": "test@example.com",
        "email_verified": True,
        "sub": "12345",
    }

    mock_verify = mocker.patch(
        "src.services.oauth_service.id_token.verify_oauth2_token",
        return_value=expected_payload,
    )
    mock_request_cls = mocker.patch("src.services.oauth_service.requests.Request")
    mock_config = mocker.patch("src.services.oauth_service.config")
    mock_config.GOOGLE_CLIENT_ID = "test_client_id"

    result = oauth_service.check_google_token(token)

    assert result == expected_payload
    mock_verify.assert_called_once_with(
        token, mock_request_cls.return_value, mock_config.GOOGLE_CLIENT_ID
    )


def test_check_google_token_value_error(oauth_service, mocker):
    """Тест: Ошибка GoogleTokenInvalidException, если токен невалиден (библиотека кидает ValueError)."""
    mocker.patch(
        "src.services.oauth_service.id_token.verify_oauth2_token",
        side_effect=ValueError("Invalid token"),
    )
    mocker.patch("src.services.oauth_service.requests.Request")
    mocker.patch("src.services.oauth_service.config")

    with pytest.raises(GoogleTokenInvalidException):
        oauth_service.check_google_token("bad_token")


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param({"email_verified": True}, id="not_field_email"),
        pytest.param(
            {"email": "test@example.com", "email_verified": False},
            id="email_is_not_verified",
        ),
        pytest.param({"email": "test@example.com"}, id="not_field_email_verified"),
        pytest.param({}, id="empty"),
    ],
)
def test_check_google_token_invalid_payload(oauth_service, mocker, payload):
    """Тест: Ошибка GoogleTokenInvalidException, если в полезной нагрузке нет email или он не подтвержден."""
    mocker.patch(
        "src.services.oauth_service.id_token.verify_oauth2_token", return_value=payload
    )
    mocker.patch("src.services.oauth_service.requests.Request")
    mocker.patch("src.services.oauth_service.config")

    with pytest.raises(GoogleTokenInvalidException):
        oauth_service.check_google_token("some_token")
