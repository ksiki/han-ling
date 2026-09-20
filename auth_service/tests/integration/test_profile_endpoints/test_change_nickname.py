import pytest
from httpx import AsyncClient
from sqlalchemy import select

from src.models import UserORM

CHANGE_NICKNAME_URL = "/api/v1/profiles/me/change-nickname"


@pytest.mark.asyncio
async def test_change_nickname_success(
    client: AsyncClient, test_user, user_session, db_session_maker
):
    """Успешное изменение никнейма текущего пользователя."""
    client.cookies.set("access_token", user_session["access_token"])

    response = await client.patch(
        CHANGE_NICKNAME_URL, json={"nickname": "new_nickname_123"}
    )

    assert response.status_code == 200

    session = db_session_maker()
    user = (
        (await session.execute(select(UserORM).where(UserORM.id == test_user.id)))
        .scalars()
        .first()
    )
    assert user.nickname == "new_nickname_123"
    await session.close()


@pytest.mark.asyncio
async def test_change_nickname_without_token(client: AsyncClient):
    """Отказ при отсутствии access-токена."""
    response = await client.patch(
        CHANGE_NICKNAME_URL, json={"nickname": "new_nickname_123"}
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_change_nickname_invalid(client: AsyncClient, user_session):
    """Отказ при никнейме, нарушающем допустимый формат."""
    client.cookies.set("access_token", user_session["access_token"])

    response = await client.patch(
        CHANGE_NICKNAME_URL, json={"nickname": "invalid_nickname!"}
    )

    assert response.status_code == 422
