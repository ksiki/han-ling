import pytest
from httpx import AsyncClient
from sqlalchemy import select

from src.models import UserSessionORM

LOGIN_URL = "/api/v1/login"


@pytest.mark.asyncio
async def test_login_success(
    client: AsyncClient, test_user, mock_captcha_success, db_session_maker
):
    """
    Успешная авторизация:
    1. Капча валидна.
    2. Пароль совпадает.
    3. Создается сессия в БД.
    4. Устанавливаются HttpOnly cookies.
    """
    payload = {
        "email": test_user.email,
        "password": "StrongPass123!",
        "captcha_token": "dummy_valid_token",
    }

    response = await client.post(LOGIN_URL, json=payload)

    assert response.status_code == 200

    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies

    session = db_session_maker()
    result = await session.execute(
        select(UserSessionORM).where(UserSessionORM.user_id == test_user.id)
    )
    user_session = result.scalars().first()

    assert user_session is not None
    assert user_session.is_active is True
    assert user_session.is_revoked is False

    await session.close()


@pytest.mark.asyncio
async def test_login_invalid_password(
    client: AsyncClient, test_user, mock_captcha_success
):
    """Отказ в авторизации при неверном пароле."""
    payload = {
        "email": test_user.email,
        "password": "WrongPassword123!",
        "captcha_token": "dummy_valid_token",
    }

    response = await client.post(LOGIN_URL, json=payload)

    assert response.status_code in (400, 401)

    assert "access_token" not in response.cookies


@pytest.mark.asyncio
async def test_login_invalid_captcha(client: AsyncClient, test_user, mock_captcha_fail):
    """Отказ в авторизации при невалидном токене Turnstile."""
    payload = {
        "email": test_user.email,
        "password": "StrongPass123!",
        "captcha_token": "invalid_hacker_token",
    }

    response = await client.post(LOGIN_URL, json=payload)

    assert response.status_code in (400, 403)  # CaptchaInvalidException
    assert "access_token" not in response.cookies


@pytest.mark.asyncio
async def test_login_user_not_found(client: AsyncClient, mock_captcha_success):
    """Отказ в авторизации, если email отсутствует в БД."""
    payload = {
        "email": "not_exist@example.com",
        "password": "SomePassword123!",
        "captcha_token": "dummy_valid_token",
    }

    response = await client.post(LOGIN_URL, json=payload)

    # PasswordOrEmailInvalidException
    assert response.status_code in (400, 401)
