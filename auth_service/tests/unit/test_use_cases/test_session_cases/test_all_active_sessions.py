import datetime
import uuid
from unittest.mock import MagicMock

from src.schemas.login import SessionItemResponse


async def test_all_active_sessions_success(session_cases, mock_uow):
    """Тест: Успешное получение списка активных сессий с корректной отметкой текущей сессии."""
    user_id = uuid.uuid4()
    current_session_id = uuid.uuid4()
    other_session_id = uuid.uuid4()

    mock_session_1 = MagicMock()
    mock_session_1.id = current_session_id
    mock_session_1.ip_address = "127.0.0.1"
    mock_session_1.user_agent = "Test Agent 1"
    mock_session_1.created_at = datetime.datetime.now(datetime.UTC)

    mock_session_2 = MagicMock()
    mock_session_2.id = other_session_id
    mock_session_2.ip_address = "192.168.1.1"
    mock_session_2.user_agent = "Test Agent 2"
    mock_session_2.created_at = datetime.datetime.now(datetime.UTC)

    mock_uow.user_session.all_active_sessions.return_value = [
        mock_session_1,
        mock_session_2,
    ]

    result = await session_cases.all_active_sessions(
        currents_session_id=current_session_id, user_id=user_id
    )

    assert len(result) == 2

    assert isinstance(result[0], SessionItemResponse)
    assert result[0].id == current_session_id
    assert result[0].ip_address == "127.0.0.1"
    assert result[0].is_current is True

    assert isinstance(result[1], SessionItemResponse)
    assert result[1].id == other_session_id
    assert result[1].ip_address == "192.168.1.1"
    assert result[1].is_current is False

    mock_uow.user_session.all_active_sessions.assert_called_once_with(user_id=user_id)


async def test_all_active_sessions_empty(session_cases, mock_uow):
    """Тест: Возврат пустого списка, если у пользователя нет активных сессий."""
    user_id = uuid.uuid4()
    current_session_id = uuid.uuid4()

    mock_uow.user_session.all_active_sessions.return_value = []

    result = await session_cases.all_active_sessions(
        currents_session_id=current_session_id, user_id=user_id
    )

    assert result == []
    mock_uow.user_session.all_active_sessions.assert_called_once_with(user_id=user_id)
