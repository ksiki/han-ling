from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core.exceptions import OTPInvalidException


async def test_finish_registration_success(registration_cases, mock_uow):
    """Тест: Успешное завершение регистрации, создание пользователя и сессии."""
    registration_cases._otp_service.verify_registration_otp = AsyncMock(
        return_value="hashed_password"
    )
    mock_user = MagicMock()
    registration_cases._registration_service.create_user = AsyncMock(
        return_value=mock_user
    )
    registration_cases._session_service.create_session = AsyncMock(
        return_value=("access_token", "refresh_token")
    )

    result = await registration_cases.finish_registration(
        email="test@example.com",
        otp="123456",
        ip="192.168.1.1",
        user_agent="Mozilla/5.0",
    )

    assert result == ("access_token", "refresh_token")
    registration_cases._otp_service.verify_registration_otp.assert_called_once_with(
        email="test@example.com", otp="123456"
    )
    registration_cases._registration_service.create_user.assert_called_once_with(
        email="test@example.com", password_hash="hashed_password"
    )
    registration_cases._session_service.create_session.assert_called_once_with(
        user=mock_user, ip="192.168.1.1", user_agent="Mozilla/5.0"
    )
    mock_uow.commit.assert_called_once()


async def test_finish_registration_invalid_otp(registration_cases, mock_uow):
    """Тест: Провал и выброс OTPInvalidException, если OTP неверен или истек."""
    registration_cases._otp_service.verify_registration_otp = AsyncMock(
        side_effect=OTPInvalidException
    )
    registration_cases._registration_service.create_user = AsyncMock()
    registration_cases._session_service.create_session = AsyncMock()

    with pytest.raises(OTPInvalidException):
        await registration_cases.finish_registration(
            email="test@example.com",
            otp="wrong_otp",
            ip="192.168.1.1",
            user_agent="Mozilla/5.0",
        )

    registration_cases._otp_service.verify_registration_otp.assert_called_once_with(
        email="test@example.com", otp="wrong_otp"
    )
    registration_cases._registration_service.create_user.assert_not_called()
    registration_cases._session_service.create_session.assert_not_called()
    mock_uow.commit.assert_not_called()
