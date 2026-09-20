import pytest
from httpx import AsyncClient
from sqlalchemy import select

from src.models import UserORM

SEND_OTP_URL = "/api/v1/register/send-otp"
VERIFY_URL = "/api/v1/register/verify"


@pytest.mark.asyncio
async def test_verify_success(
    client: AsyncClient,
    db_session_maker,
    fake_redis,
    mock_captcha_success,
    mock_email_success,
    mocker,
):
    """Успешное завершение регистрации с созданием пользователя и выдачей токенов."""
    mocker.patch("src.services.otp_service.random.randint", return_value=123456)
    email = "new_user@example.com"

    send_response = await client.post(
        SEND_OTP_URL,
        json={
            "email": email,
            "password": "StrongPass123!",
            "captcha_token": "dummy_valid_token",
        },
    )
    assert send_response.status_code == 200

    response = await client.post(VERIFY_URL, json={"email": email, "otp": "123456"})

    assert response.status_code == 201
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies

    session = db_session_maker()
    user = (
        (await session.execute(select(UserORM).where(UserORM.email == email)))
        .scalars()
        .first()
    )
    assert user is not None
    await session.close()


@pytest.mark.asyncio
async def test_verify_invalid_otp(
    client: AsyncClient,
    fake_redis,
    mock_captcha_success,
    mock_email_success,
    mocker,
):
    """Отказ при неверном OTP-коде."""
    mocker.patch("src.services.otp_service.random.randint", return_value=123456)
    email = "new_user@example.com"

    send_response = await client.post(
        SEND_OTP_URL,
        json={
            "email": email,
            "password": "StrongPass123!",
            "captcha_token": "dummy_valid_token",
        },
    )
    assert send_response.status_code == 200

    response = await client.post(VERIFY_URL, json={"email": email, "otp": "000000"})

    assert response.status_code == 400
    assert "access_token" not in response.cookies
