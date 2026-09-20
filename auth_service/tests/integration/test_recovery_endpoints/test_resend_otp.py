import pytest
from httpx import AsyncClient

SEND_OTP_URL = "/api/v1/password-reset/send-otp"
RESEND_OTP_URL = "/api/v1/password-reset/resend-otp"


@pytest.mark.asyncio
async def test_resend_otp_success(
    client: AsyncClient, fake_redis, mock_captcha_success, mock_email_success
):
    """Повторная отправка OTP при существующем состоянии сброса."""
    email = "reset_user@example.com"

    send_response = await client.post(
        SEND_OTP_URL,
        json={"email": email, "captcha_token": "dummy_valid_token"},
    )
    assert send_response.status_code == 200

    response = await client.post(RESEND_OTP_URL, json={"email": email})

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_resend_otp_without_state(client: AsyncClient, fake_redis):
    """Отказ при отсутствии предыдущего состояния сброса."""
    response = await client.post(RESEND_OTP_URL, json={"email": "unknown@example.com"})

    assert response.status_code == 400
