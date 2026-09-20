import datetime
import uuid

import fakeredis
import jwt
import pytest_asyncio
import respx
from httpx import Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_redis_client
from src.core.security import get_password_hash
from src.core.settings import config
from src.main import app
from src.models import UserORM, UserSessionORM


@pytest_asyncio.fixture
async def test_user(db_session_maker) -> UserORM:
    """Создает тестового пользователя с известным паролем в базе данных."""
    session: AsyncSession = db_session_maker()
    user = UserORM(
        email="test_user@example.com",
        password_hash=get_password_hash("StrongPass123!"),
        nickname="test_middle_dev",
        is_active=True,
        is_deleted=False,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    await session.close()
    return user


@pytest_asyncio.fixture
def mock_captcha_success(respx_mock: respx.MockRouter) -> None:
    """Мокирует успешный ответ от API Cloudflare Turnstile."""
    respx_mock.post(config.CLOUDFLARE_VERIFY_URL).mock(
        return_value=Response(status_code=200, json={"success": True})
    )


@pytest_asyncio.fixture
def mock_captcha_fail(respx_mock: respx.MockRouter) -> None:
    """Мокирует отказ валидации капчи от API Cloudflare."""
    respx_mock.post(config.CLOUDFLARE_VERIFY_URL).mock(
        return_value=Response(
            status_code=200,
            json={"success": False, "error-codes": ["invalid-input-response"]},
        )
    )


@pytest_asyncio.fixture
async def user_session(db_session_maker, test_user) -> dict:
    """Создает активную сессию test_user и возвращает валидные access/refresh токены."""
    session: AsyncSession = db_session_maker()

    jti = uuid.uuid4()
    now = datetime.datetime.now(datetime.UTC)
    expires_at = now + datetime.timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS)

    user_session = UserSessionORM(
        user_id=test_user.id,
        refresh_token_jti=str(jti),
        user_agent="pytest-agent",
        ip_address="127.0.0.1",
        expires_at=expires_at,
    )
    session.add(user_session)
    await session.commit()
    await session.refresh(user_session)

    access_token = jwt.encode(
        {
            "sub": str(test_user.id),
            "jti": str(uuid.uuid4()),
            "session_id": str(user_session.id),
            "role": test_user.role.value,
            "nickname": test_user.nickname,
            "exp": now + datetime.timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES),
            "type": "access",
        },
        key=config.SECRET_KEY,
        algorithm=config.ALGORITHM,
    )
    refresh_token = jwt.encode(
        {
            "sub": str(test_user.id),
            "jti": str(jti),
            "exp": expires_at,
            "type": "refresh",
        },
        key=config.SECRET_KEY,
        algorithm=config.ALGORITHM,
    )

    await session.close()
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "session": user_session,
    }


@pytest_asyncio.fixture
def fake_redis() -> fakeredis.FakeAsyncRedis:
    """Подменяет зависимость get_redis_client на fakeredis."""
    redis = fakeredis.FakeAsyncRedis(decode_responses=True)
    app.dependency_overrides[get_redis_client] = lambda: redis
    yield redis
    app.dependency_overrides.pop(get_redis_client, None)


@pytest_asyncio.fixture
def mock_email_success(respx_mock: respx.MockRouter) -> None:
    """Мокирует успешную отправку письма через Resend API."""
    respx_mock.post(config.RESEND_URL).mock(
        return_value=Response(status_code=200, json={})
    )
