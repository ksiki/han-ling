import pytest
from httpx import AsyncClient

ME_URL = "/api/v1/profiles/me"


@pytest.mark.asyncio
async def test_get_me_success(client: AsyncClient, test_user, user_session):
    """Возвращает профиль текущего аутентифицированного пользователя."""
    client.cookies.set("access_token", user_session["access_token"])

    response = await client.get(ME_URL)

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == str(test_user.id)
    assert data["email"] == test_user.email
    assert data["nickname"] == test_user.nickname
    assert data["role"] == "USER"


@pytest.mark.asyncio
async def test_get_me_without_token(client: AsyncClient):
    """Отказ при отсутствии access-токена."""
    response = await client.get(ME_URL)

    assert response.status_code == 401
