import datetime
import uuid
from unittest.mock import MagicMock

import pytest

from src.core.exceptions import UserBannedOrDeletedException
from src.models import UserORM


async def test_create_session_success_no_revoke(
    session_service, mock_uow, mock_config, mocker
):
    """Тест: Успешное создание сессии. Лимит не превышен, старые сессии не отзываются."""
    user_id = uuid.uuid4()
    mock_user = MagicMock(spec=UserORM)
    mock_user.id = user_id
    mock_user.is_valid = True
    mock_user.role.value = "user"
    mock_user.nickname = "user_123"

    mock_config.MAX_ACTIVE_SESSIONS = 5

    mock_uow.user_session.all_active_sessions.return_value = [MagicMock(), MagicMock()]

    jti = uuid.uuid4()
    expires_at = datetime.datetime.now(datetime.UTC)
    mocker.patch.object(
        session_service,
        "_create_refresh_token",
        return_value=("refresh_token_str", jti, expires_at),
    )
    mocker.patch.object(
        session_service, "create_access_token", return_value="access_token_str"
    )

    mock_new_session = MagicMock()
    mock_new_session.id = uuid.uuid4()
    mock_uow.user_session.add.return_value = mock_new_session

    access, refresh = await session_service.create_session(
        user=mock_user, ip="127.0.0.1", user_agent="Mozilla/5.0"
    )

    assert access == "access_token_str"
    assert refresh == "refresh_token_str"

    mock_uow.user_session.all_active_sessions.assert_called_once_with(user_id=user_id)

    for session_mock in mock_uow.user_session.all_active_sessions.return_value:
        session_mock.revoke.assert_not_called()

    mock_uow.user_session.add.assert_called_once()
    mock_uow.flush.assert_called_once()

    session_service.create_access_token.assert_called_once_with(
        user_id=user_id,
        session_id=mock_new_session.id,
        user_role="user",
        user_nickname="user_123",
    )


async def test_create_session_success_with_revoke(
    session_service, mock_uow, mock_config, mocker
):
    """Тест: Успешное создание сессии с превышением лимита (отзыв старых сессий)."""
    user_id = uuid.uuid4()
    mock_user = MagicMock(spec=UserORM)
    mock_user.id = user_id
    mock_user.is_valid = True
    mock_user.role.value = "admin"
    mock_user.nickname = "user_admin"

    # У пользователя 3 активные сессии (равно лимиту).
    # При добавлении новой, 1 старая должна быть отозвана (3 - 3 + 1 = 1).
    active_sessions = [MagicMock(), MagicMock(), MagicMock()]
    mock_uow.user_session.all_active_sessions.return_value = active_sessions

    mocker.patch.object(
        session_service,
        "_create_refresh_token",
        return_value=("refresh", uuid.uuid4(), datetime.datetime.now(datetime.UTC)),
    )
    mocker.patch.object(session_service, "create_access_token", return_value="access")
    mock_uow.user_session.add.return_value = MagicMock(id=uuid.uuid4())

    await session_service.create_session(
        user=mock_user, ip="192.168.1.1", user_agent="Chrome"
    )

    # Проверяем, что revoke вызван только у последней сессии в списке (active_sessions[-1:])
    active_sessions[0].revoke.assert_not_called()
    active_sessions[1].revoke.assert_not_called()
    active_sessions[2].revoke.assert_called_once_with(reason="exceeding the limit")

    mock_uow.user_session.add.assert_called_once()
    mock_uow.flush.assert_called_once()


async def test_create_session_user_banned(
    session_service, mock_uow, mock_config, mocker
):
    """Тест: Ошибка UserBannedOrDeletedException, если пользователь не валиден."""
    mock_user = MagicMock(spec=UserORM)
    mock_user.is_valid = False

    with pytest.raises(UserBannedOrDeletedException):
        await session_service.create_session(
            user=mock_user, ip="127.0.0.1", user_agent="test"
        )

    mock_uow.user_session.all_active_sessions.assert_not_called()
    mock_uow.user_session.add.assert_not_called()
