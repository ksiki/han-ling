import datetime
import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from src.core.security import get_password_hash
from src.models import UserORM, UserSessionORM


@pytest.mark.asyncio
async def test_revoke_own_session(client: AsyncClient, user_session, db_session_maker):
    """Отзыв собственной сессии по ее идентификатору."""
    client.cookies.set("access_token", user_session["access_token"])

    response = await client.delete(f"/api/v1/sessions/{user_session['session'].id}")

    assert response.status_code == 200

    session = db_session_maker()
    result = await session.execute(
        select(UserSessionORM).where(UserSessionORM.id == user_session["session"].id)
    )
    session_orm = result.scalars().first()

    assert session_orm.is_revoked is True
    assert session_orm.revoked_reason == "revoke from another session"

    await session.close()


@pytest.mark.asyncio
async def test_revoke_other_user_session(
    client: AsyncClient, user_session, db_session_maker
):
    """Отказ при попытке отозвать сессию другого пользователя."""
    session = db_session_maker()

    other_user = UserORM(
        email="other_user@example.com",
        password_hash=get_password_hash("StrongPass123!"),
        nickname="other_dev",
        is_active=True,
        is_deleted=False,
    )
    session.add(other_user)
    await session.commit()
    await session.refresh(other_user)

    other_session = UserSessionORM(
        user_id=other_user.id,
        refresh_token_jti=str(uuid.uuid4()),
        expires_at=datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=15),
    )
    session.add(other_session)
    await session.commit()
    await session.refresh(other_session)

    client.cookies.set("access_token", user_session["access_token"])

    response = await client.delete(f"/api/v1/sessions/{other_session.id}")

    assert response.status_code == 400

    await session.close()


@pytest.mark.asyncio
async def test_revoke_nonexistent_session(client: AsyncClient, user_session):
    """Отказ при отзыве несуществующей сессии."""
    client.cookies.set("access_token", user_session["access_token"])

    response = await client.delete(f"/api/v1/sessions/{uuid.uuid4()}")

    assert response.status_code == 400
