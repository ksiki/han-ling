import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from shared.exceptions import InvalidTokenException


async def test_update_access_token_success(auth_cases, mock_uow):
    """Тест: Успешное обновление access токена по валидному jti сессии."""
    user_id = uuid.uuid4()
    user_role = "user"
    refresh_jti = uuid.uuid4()

    mock_session = MagicMock()
    mock_session.id = uuid.uuid4()
    mock_uow.user_session.get_by_jti = AsyncMock(return_value=mock_session)
    auth_cases._session_service.create_access_token = MagicMock(
        return_value="new_access_token"
    )

    result = await auth_cases.update_access_token(
        user_id=user_id, user_role=user_role, refresh_jti=refresh_jti
    )

    assert result == "new_access_token"
    mock_uow.user_session.get_by_jti.assert_called_once_with(jti=refresh_jti)
    auth_cases._session_service.create_access_token.assert_called_once_with(
        user_id=user_id, session_id=mock_session.id, user_role=user_role
    )


async def test_update_access_token_session_not_found(auth_cases, mock_uow):
    """Тест: Провал при отсутствии сессии с переданным jti в базе данных."""
    user_id = uuid.uuid4()
    user_role = "user"
    refresh_jti = uuid.uuid4()

    mock_uow.user_session.get_by_jti = AsyncMock(side_effect=InvalidTokenException)
    auth_cases._session_service.create_access_token = MagicMock()

    with pytest.raises(InvalidTokenException):
        await auth_cases.update_access_token(
            user_id=user_id, user_role=user_role, refresh_jti=refresh_jti
        )

    mock_uow.user_session.get_by_jti.assert_called_once_with(jti=refresh_jti)
    auth_cases._session_service.create_access_token.assert_not_called()
