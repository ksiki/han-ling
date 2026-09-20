import uuid
from unittest.mock import MagicMock

import pytest

from src.core.exceptions import SessionInvalidException


async def test_revoke_session_by_id_success_with_user(session_cases, mock_uow):
    """Тест: Успешный отзыв сессии с передачей user_id (причина - revoke from another session)."""
    session_id = uuid.uuid4()
    user_id = uuid.uuid4()
    mock_session = MagicMock()
    mock_session.user_id = user_id
    mock_uow.user_session.get_or_none.return_value = mock_session

    await session_cases.revoke_session_by_id(session_id=session_id, user_id=user_id)

    mock_uow.user_session.get_or_none.assert_called_once_with(id=session_id)
    mock_session.revoke.assert_called_once_with(reason="revoke from another session")
    mock_uow.commit.assert_called_once()


async def test_revoke_session_by_id_success_without_user(session_cases, mock_uow):
    """Тест: Успешный отзыв сессии без передачи user_id (причина - logout)."""
    session_id = uuid.uuid4()
    mock_session = MagicMock()
    mock_uow.user_session.get_or_none.return_value = mock_session

    await session_cases.revoke_session_by_id(session_id=session_id)

    mock_uow.user_session.get_or_none.assert_called_once_with(id=session_id)
    mock_session.revoke.assert_called_once_with(reason="logout")
    mock_uow.commit.assert_called_once()


async def test_revoke_session_by_id_not_found(session_cases, mock_uow):
    """Тест: Провал и выброс SessionInvalidException, если сессия не найдена."""
    session_id = uuid.uuid4()
    mock_uow.user_session.get_or_none.return_value = None

    with pytest.raises(SessionInvalidException):
        await session_cases.revoke_session_by_id(session_id=session_id)

    mock_uow.user_session.get_or_none.assert_called_once_with(id=session_id)
    mock_uow.commit.assert_not_called()


async def test_revoke_session_by_id_wrong_user(session_cases, mock_uow):
    """Тест: Провал и выброс SessionInvalidException, если сессия принадлежит другому пользователю."""
    session_id = uuid.uuid4()
    user_id = uuid.uuid4()
    mock_session = MagicMock()
    mock_session.user_id = uuid.uuid4()
    mock_uow.user_session.get_or_none.return_value = mock_session

    with pytest.raises(SessionInvalidException):
        await session_cases.revoke_session_by_id(session_id=session_id, user_id=user_id)

    mock_uow.user_session.get_or_none.assert_called_once_with(id=session_id)
    mock_session.revoke.assert_not_called()
    mock_uow.commit.assert_not_called()
