from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.api.dependencies import get_registration_cases
from src.main import app


@pytest_asyncio.fixture
async def unit_client(
    mock_registration_cases,
) -> AsyncGenerator[AsyncClient, Any, None]:
    app.dependency_overrides[get_registration_cases] = lambda: mock_registration_cases

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://testserver/auth/api/v1"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
def mock_registration_cases() -> AsyncMock:
    mock = AsyncMock()
    mock.begin_registration.return_value = "123456"
    mock.resend_otp.return_value = "654321"
    mock.finish_registration.return_value = (
        "access_token_template",
        "refresh_token_template",
    )
    return mock


@pytest.fixture
def mock_send_email(mocker) -> AsyncMock:
    return mocker.patch("src.api.v1.endpoints.registration.send_otp_email")


@pytest.fixture
def mock_set_auth_cookies(mocker) -> MagicMock:
    return mocker.patch("src.api.v1.endpoints.registration.set_auth_cookies")
