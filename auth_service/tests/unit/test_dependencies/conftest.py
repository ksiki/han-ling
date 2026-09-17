from unittest.mock import AsyncMock

import pytest


@pytest.fixture
def fake_uow() -> AsyncMock:
    uow = AsyncMock()
    uow.user = AsyncMock()
    return uow
