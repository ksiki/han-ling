import uuid
from unittest.mock import MagicMock

import pytest
from shared.exceptions import InvalidTokenException

from src.api.dependencies import _check_refresh_session


async def test_check_refresh_session_success(fake_uow) -> None:
    test_jti = uuid.uuid4()

    fake_session = MagicMock()
    fake_session.is_active = True

    fake_uow.user_session.get_by_jti.return_value = fake_session

    await _check_refresh_session(uow=fake_uow, jti=test_jti)

    fake_uow.user_session.get_by_jti.assert_awaited_once_with(jti=test_jti)


@pytest.mark.parametrize(
    "fake_session, expected_exception",
    [
        pytest.param(
            None,
            InvalidTokenException,
            id="session_not_found",
        ),
        pytest.param(
            MagicMock(is_active=False),
            InvalidTokenException,
            id="session_is_not_active",
        ),
    ],
)
async def test_check_refresh_session_failes(
    fake_uow, fake_session, expected_exception
) -> None:
    test_jti = uuid.uuid4()

    fake_uow.user_session.get_by_jti.return_value = fake_session
    with pytest.raises(expected_exception):
        await _check_refresh_session(uow=fake_uow, jti=test_jti)
