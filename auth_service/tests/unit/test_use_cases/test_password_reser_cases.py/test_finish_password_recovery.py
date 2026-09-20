from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core.exceptions import OTPInvalidException, UserNotFoundException


async def test_finish_password_recovery_success(password_reset_cases, mock_uow):
    """Тест: Успешное завершение восстановления пароля и создание сессии."""
    password_reset_cases._otp_service.verify_reset_otp = AsyncMock()
    mock_user = MagicMock()
    password_reset_cases._recovery_service.change_password_by_email = AsyncMock(
        return_value=mock_user
    )
    password_reset_cases._session_service.create_session = AsyncMock(
        return_value=("access_token", "refresh_token")
    )

    result = await password_reset_cases.finish_password_recovery(
        email="test@example.com",
        otp="123456",
        new_password="new_secure_password",
        ip="192.168.1.1",
        user_agent="Mozilla",
    )

    assert result == ("access_token", "refresh_token")
    password_reset_cases._otp_service.verify_reset_otp.assert_called_once_with(
        email="test@example.com", otp="123456"
    )
    password_reset_cases._recovery_service.change_password_by_email.assert_called_once_with(
        email="test@example.com", new_password="new_secure_password"
    )
    password_reset_cases._session_service.create_session.assert_called_once_with(
        user=mock_user, ip="192.168.1.1", user_agent="Mozilla"
    )
    mock_uow.commit.assert_called_once()


async def test_finish_password_recovery_invalid_otp(password_reset_cases, mock_uow):
    """Тест: Провал и выброс OTPInvalidException при неверном или истекшем коде."""
    password_reset_cases._otp_service.verify_reset_otp = AsyncMock(
        side_effect=OTPInvalidException
    )
    password_reset_cases._recovery_service.change_password_by_email = AsyncMock()

    with pytest.raises(OTPInvalidException):
        await password_reset_cases.finish_password_recovery(
            email="test@example.com",
            otp="wrong",
            new_password="new_secure_password",
            ip="192.168.1.1",
            user_agent="Mozilla",
        )

    password_reset_cases._recovery_service.change_password_by_email.assert_not_called()
    mock_uow.commit.assert_not_called()


async def test_finish_password_recovery_user_not_found(password_reset_cases, mock_uow):
    """Тест: Провал и выброс UserNotFoundException, если пользователь не существует."""
    password_reset_cases._otp_service.verify_reset_otp = AsyncMock()
    password_reset_cases._recovery_service.change_password_by_email = AsyncMock(
        side_effect=UserNotFoundException
    )
    password_reset_cases._session_service.create_session = AsyncMock()

    with pytest.raises(UserNotFoundException):
        await password_reset_cases.finish_password_recovery(
            email="notfound@example.com",
            otp="123456",
            new_password="new_secure_password",
            ip="192.168.1.1",
            user_agent="Mozilla",
        )

    password_reset_cases._session_service.create_session.assert_not_called()
    mock_uow.commit.assert_not_called()
