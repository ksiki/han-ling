from unittest.mock import AsyncMock, MagicMock

import pytest

from src.background_tasks.email import send_otp_email


@pytest.fixture
def mock_http_client(mocker):
    mock = mocker.patch("src.background_tasks.email.http_client")
    mock.post = AsyncMock()
    return mock


@pytest.fixture
def mock_logger(mocker):
    return mocker.patch("src.background_tasks.email.logger")


@pytest.fixture
def mock_config(mocker):
    config_mock = mocker.patch("src.background_tasks.email.config")
    config_mock.DOMAIN = "test.com"
    config_mock.PRODUCT_NAME = "TestProduct"
    config_mock.RESEND_API_KEY = "test_api_key"
    config_mock.RESEND_URL = "https://api.resend.com/emails"
    return config_mock


async def test_send_otp_email_success(mock_http_client, mock_logger, mock_config):
    email = "test@example.com"
    otp = "123456"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_http_client.post.return_value = mock_response

    await send_otp_email(email_to=email, otp_code=otp)

    expected_payload = {
        "from": f"noreply@{mock_config.DOMAIN}",
        "to": [email],
        "subject": f"Ваш код подтверждения | {mock_config.PRODUCT_NAME}",
        "html": f"Ваш проверочный код: {otp}\nКод действителен ограниченное время.",
    }
    expected_headers = {
        "Authorization": f"Bearer {mock_config.RESEND_API_KEY}",
        "Content-Type": "application/json",
    }

    mock_http_client.post.assert_called_once_with(
        mock_config.RESEND_URL, json=expected_payload, headers=expected_headers
    )

    mock_logger.info.assert_called_once_with(f"OTP send to {email} is successful")


async def test_send_otp_email_failure(mock_http_client, mock_logger, mock_config):
    email = "fail@example.com"
    otp = "654321"

    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    mock_http_client.post.return_value = mock_response

    await send_otp_email(email_to=email, otp_code=otp)

    mock_http_client.post.assert_called_once()

    mock_logger.info.assert_called_once_with(
        f"Resend API Error: {mock_response.text}. Sent OTP to {email} failed"
    )
