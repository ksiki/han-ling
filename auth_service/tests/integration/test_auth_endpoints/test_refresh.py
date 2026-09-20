import pytest
from httpx import AsyncClient
from sqlalchemy import select

from src.models import UserSessionORM

REFRESH_URL = "/api/v1/refresh"


@pytest.mark.asyncio
async def test_refresh_success(client: AsyncClient, user_session):
    """Обновление access-токена по валидному refresh-токену."""
    client.cookies.set("refresh_token", user_session["refresh_token"])

    response = await client.post(REFRESH_URL)

    assert response.status_code == 200
    assert "access_token" in response.cookies


@pytest.mark.asyncio
async def test_refresh_without_token(client: AsyncClient):
    """Отказ в обновлении при отсутствии refresh-токена."""
    response = await client.post(REFRESH_URL)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_with_revoked_session(
    client: AsyncClient, user_session, db_session_maker
):
    """Отказ в обновлении при отозванной сессии."""
    session = db_session_maker()
    result = await session.execute(
        select(UserSessionORM).where(UserSessionORM.id == user_session["session"].id)
    )
    session_orm = result.scalars().first()
    session_orm.revoke(reason="test")
    await session.commit()

    client.cookies.set("refresh_token", user_session["refresh_token"])

    response = await client.post(REFRESH_URL)

    assert response.status_code == 401
    await session.close()
