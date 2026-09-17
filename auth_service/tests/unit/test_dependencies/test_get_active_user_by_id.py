import uuid
from unittest.mock import MagicMock

import pytest
from shared.exceptions import InvalidTokenException

from src.api.dependencies import _get_active_user_by_id
from src.core.exceptions import UserBannedOrDeletedException


async def test_get_active_user_by_id_success(fake_uow) -> None:
    test_uuid = uuid.uuid4()

    fake_user = MagicMock()
    fake_user.id = test_uuid
    fake_user.is_valid = True

    fake_uow.user.get_or_none.return_value = fake_user

    user = await _get_active_user_by_id(user_id=test_uuid, uow=fake_uow)
    fake_uow.user.get_or_none.assert_awaited_once_with(id=test_uuid)

    assert user is fake_user


@pytest.mark.parametrize(
    "fake_user, expected_exception",
    [
        pytest.param(
            None,
            InvalidTokenException,
            id="user_not_found",
        ),
        pytest.param(
            MagicMock(is_valid=False),
            UserBannedOrDeletedException,
            id="user_banned_or_deleted",
        ),
    ],
)
async def test_get_active_user_by_id_failed(
    fake_uow, fake_user, expected_exception
) -> None:
    test_uuid = uuid.uuid4()

    fake_uow.user.get_or_none.return_value = fake_user
    with pytest.raises(expected_exception):
        await _get_active_user_by_id(user_id=test_uuid, uow=fake_uow)

    fake_uow.user.get_or_none.assert_awaited_once_with(id=test_uuid)
