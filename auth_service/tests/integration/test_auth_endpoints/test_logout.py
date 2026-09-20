import pytest
from httpx import AsyncClient
from sqlalchemy import select

from src.models import UserSessionORM

LOGOUT_URL = "/api/v1/logout"


@pytest.mark.asyncio
async def test_logout_success(client: AsyncClient, user_session, db_session_maker):
    """Завершает текущую сессию и отзывает ее в базе данных."""
    client.cookies.set("access_token", user_session["access_token"])

    response = await client.post(LOGOUT_URL)

    assert response.status_code == 200

    session = db_session_maker()
    result = await session.execute(
        select(UserSessionORM).where(UserSessionORM.id == user_session["session"].id)
    )
    session_orm = result.scalars().first()

    assert session_orm.is_revoked is True
    assert session_orm.revoked_reason == "logout"

    await session.close()


@pytest.mark.asyncio
async def test_logout_without_token(client: AsyncClient):
    """Отказ при отсутствии access-токена."""
    response = await client.post(LOGOUT_URL)

    assert response.status_code == 401
