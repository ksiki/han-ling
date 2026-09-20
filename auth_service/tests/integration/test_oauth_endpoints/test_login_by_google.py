import pytest
from httpx import AsyncClient
from sqlalchemy import select

from src.models import ProviderEnum, UserORM, UserProviderORM

LOGIN_URL = "/api/v1/google/login"


@pytest.mark.asyncio
async def test_login_by_google_success(client: AsyncClient, db_session_maker, mocker):
    """Успешный вход через Google: создается пользователь и привязка провайдера."""
    mocker.patch(
        "src.services.oauth_service.id_token.verify_oauth2_token",
        return_value={
            "email": "google_user@example.com",
            "email_verified": True,
            "sub": "google_sub_123",
        },
    )

    response = await client.post(LOGIN_URL, json={"id_token": "valid_google_token"})

    assert response.status_code == 200
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies

    session = db_session_maker()

    user = (
        (
            await session.execute(
                select(UserORM).where(UserORM.email == "google_user@example.com")
            )
        )
        .scalars()
        .first()
    )
    assert user is not None

    provider = (
        (
            await session.execute(
                select(UserProviderORM).where(
                    UserProviderORM.provider_id == "google_sub_123"
                )
            )
        )
        .scalars()
        .first()
    )
    assert provider is not None
    assert provider.provider == ProviderEnum.GOOGLE
    assert provider.user_id == user.id

    await session.close()


@pytest.mark.asyncio
async def test_login_by_google_invalid_token(client: AsyncClient, mocker):
    """Отказ при невалидном Google ID Token."""
    mocker.patch(
        "src.services.oauth_service.id_token.verify_oauth2_token",
        side_effect=ValueError("invalid token"),
    )

    response = await client.post(LOGIN_URL, json={"id_token": "invalid_token"})

    assert response.status_code == 401
    assert "access_token" not in response.cookies
