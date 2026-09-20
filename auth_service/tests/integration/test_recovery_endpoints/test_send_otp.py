import pytest
from httpx import AsyncClient

SEND_OTP_URL = "/api/v1/password-reset/send-otp"


@pytest.mark.asyncio
async def test_send_otp_success(
    client: AsyncClient, fake_redis, mock_captcha_success, mock_email_success
):
    """Успешная отправка OTP для сброса пароля."""
    response = await client.post(
        SEND_OTP_URL,
        json={"email": "reset_user@example.com", "captcha_token": "dummy_valid_token"},
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_send_otp_invalid_captcha(
    client: AsyncClient, fake_redis, mock_captcha_fail
):
    """Отказ при невалидной капче."""
    response = await client.post(
        SEND_OTP_URL,
        json={"email": "reset_user@example.com", "captcha_token": "invalid_token"},
    )

    assert response.status_code == 400
