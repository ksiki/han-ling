from unittest.mock import AsyncMock

import pytest


@pytest.fixture
def fake_uow() -> AsyncMock:
    return AsyncMock()
