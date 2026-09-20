import uuid
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from src.core.exceptions import NicknameInvalidException


async def test_change_nickname_success(profile_cases, mock_uow):
    user_id = uuid.uuid4()
    new_nickname = "new_nick"
    mock_user = MagicMock()
    mock_uow.user.get.return_value = mock_user

    await profile_cases.change_nickname(user_id=user_id, new_nickname=new_nickname)

    mock_uow.user.get.assert_called_once_with(id=user_id)
    assert mock_user.nickname == new_nickname
    mock_uow.flush.assert_called_once()
    mock_uow.commit.assert_called_once()


async def test_change_nickname_integrity_error(profile_cases, mock_uow):
    user_id = uuid.uuid4()
    mock_user = MagicMock()
    mock_uow.user.get.return_value = mock_user

    mock_uow.flush.side_effect = IntegrityError("statement", "params", "orig")

    with pytest.raises(NicknameInvalidException):
        await profile_cases.change_nickname(user_id=user_id, new_nickname="taken_nick")

    mock_uow.flush.assert_called_once()
    mock_uow.commit.assert_not_called()
