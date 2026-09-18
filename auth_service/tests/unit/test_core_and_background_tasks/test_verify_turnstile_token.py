from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from src.core.security import verify_turnstile_token


@pytest.fixture
def mock_http_client(mocker):
    mock = mocker.patch("src.core.security.http_client")
    mock.post = AsyncMock()
    return mock


@pytest.fixture
def mock_logger(mocker):
    return mocker.patch("src.core.security.logger")


@pytest.fixture
def mock_config(mocker):
    config_mock = mocker.patch("src.core.security.config")
    config_mock.CLOUDFLARE_SECRET_KEY = "test_secret"
    config_mock.CLOUDFLARE_VERIFY_URL = "https://test.cloudflare.com/verify"
    return config_mock


@pytest.mark.parametrize("invalid_token", ["", "   ", None])
async def test_verify_turnstile_token_empty(invalid_token):
    """Тест: пустой токен или пробелы сразу возвращают False без HTTP запроса."""
    result = await verify_turnstile_token(token=invalid_token)
    assert result is False


async def test_verify_turnstile_token_success(mock_http_client, mock_config):
    """Тест: успешная валидация токена с опциональными параметрами."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"success": True}
    mock_http_client.post.return_value = mock_response

    token = "valid_token"
    client_ip = "192.168.1.1"
    idempotency_key = "test-uuid"

    result = await verify_turnstile_token(
        token=token, client_ip=client_ip, idempotency_key=idempotency_key
    )

    assert result is True
    mock_http_client.post.assert_called_once_with(
        mock_config.CLOUDFLARE_VERIFY_URL,
        json={
            "secret": mock_config.CLOUDFLARE_SECRET_KEY,
            "response": token,
            "remoteip": client_ip,
            "idempotency_key": idempotency_key,
        },
    )


async def test_verify_turnstile_token_rejected(mock_http_client, mock_logger):
    """Тест: Cloudflare вернул success: False (капча не пройдена)."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "success": False,
        "error-codes": ["invalid-input-response"],
    }
    mock_http_client.post.return_value = mock_response

    result = await verify_turnstile_token(token="bad_token")

    assert result is False
    mock_logger.warning.assert_called_once_with(
        "Turnstile rejected the captcha: %s", ["invalid-input-response"]
    )


async def test_verify_turnstile_token_timeout(mock_http_client, mock_logger):
    """Тест: отлов таймаута при запросе к Cloudflare."""
    mock_http_client.post.side_effect = httpx.TimeoutException("Timeout")

    result = await verify_turnstile_token(token="some_token")

    assert result is False
    mock_logger.error.assert_called_once_with("Cloudflare Turnstile timeout")


async def test_verify_turnstile_token_network_error(mock_http_client, mock_logger):
    """Тест: отлов сетевой ошибки httpx.RequestError."""
    mock_request = MagicMock()
    mock_http_client.post.side_effect = httpx.RequestError(
        "Network Error", request=mock_request
    )

    result = await verify_turnstile_token(token="some_token")

    assert result is False
    assert (
        mock_logger.error.call_args[0][0]
        == "Network error with request of Turnstile: %s"
    )


async def test_verify_turnstile_token_invalid_json(mock_http_client, mock_logger):
    """Тест: Cloudflare вернул невалидный JSON."""
    mock_response = MagicMock()
    mock_response.json.side_effect = ValueError("No JSON object could be decoded")
    mock_response.text = "Bad Gateway"
    mock_http_client.post.return_value = mock_response

    result = await verify_turnstile_token(token="some_token")

    assert result is False
    mock_logger.error.assert_called_once_with(
        "Can't parsed JSON from Cloudflare. Response: %s", "Bad Gateway"
    )
