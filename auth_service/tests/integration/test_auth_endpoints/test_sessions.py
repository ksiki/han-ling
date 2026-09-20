import pytest
from httpx import AsyncClient

SESSIONS_URL = "/api/v1/sessions"


@pytest.mark.asyncio
async def test_get_active_sessions_success(client: AsyncClient, user_session):
    """Возвращает список активных сессий с отметкой текущей."""
    client.cookies.set("access_token", user_session["access_token"])

    response = await client.get(SESSIONS_URL)

    assert response.status_code == 200

    data = response.json()
    sessions = data["sessions"]

    assert len(sessions) == 1
    assert sessions[0]["id"] == str(user_session["session"].id)
    assert sessions[0]["is_current"] is True


@pytest.mark.asyncio
async def test_get_active_sessions_without_token(client: AsyncClient):
    """Отказ при отсутствии access-токена."""
    response = await client.get(SESSIONS_URL)

    assert response.status_code == 401
