import pytest
from httpx import AsyncClient

SEND_OTP_URL = "/api/v1/password-reset/send-otp"
CONFIRM_URL = "/api/v1/password-reset/confirm"


@pytest.mark.asyncio
async def test_confirm_success(
    client: AsyncClient,
    test_user,
    fake_redis,
    mock_captcha_success,
    mock_email_success,
    mocker,
):
    """Успешное подтверждение сброса пароля с выдачей токенов."""
    mocker.patch("src.services.otp_service.random.randint", return_value=123456)

    send_response = await client.post(
        SEND_OTP_URL,
        json={"email": test_user.email, "captcha_token": "dummy_valid_token"},
    )
    assert send_response.status_code == 200

    response = await client.post(
        CONFIRM_URL,
        json={
            "email": test_user.email,
            "otp": "123456",
            "new_password": "NewStrongPass123!",
        },
    )

    assert response.status_code == 200
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies


@pytest.mark.asyncio
async def test_confirm_invalid_otp(
    client: AsyncClient,
    test_user,
    fake_redis,
    mock_captcha_success,
    mock_email_success,
    mocker,
):
    """Отказ при неверном OTP-коде."""
    mocker.patch("src.services.otp_service.random.randint", return_value=123456)

    send_response = await client.post(
        SEND_OTP_URL,
        json={"email": test_user.email, "captcha_token": "dummy_valid_token"},
    )
    assert send_response.status_code == 200

    response = await client.post(
        CONFIRM_URL,
        json={
            "email": test_user.email,
            "otp": "000000",
            "new_password": "NewStrongPass123!",
        },
    )

    assert response.status_code == 400
    assert "access_token" not in response.cookies
