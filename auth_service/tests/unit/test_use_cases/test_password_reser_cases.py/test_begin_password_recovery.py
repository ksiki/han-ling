from unittest.mock import AsyncMock

import pytest

from src.core.exceptions import CaptchaInvalidException


async def test_begin_password_recovery_success(password_reset_cases, mocker):
    """Тест: Успешный запуск восстановления пароля при валидной капче."""
    mocker.patch(
        "src.use_cases.password_reset_cases.verify_turnstile_token", return_value=True
    )
    password_reset_cases._otp_service.create_reset_state = AsyncMock(
        return_value="123456"
    )

    result = await password_reset_cases.begin_password_recovery(
        captcha_token="valid_token", email="test@example.com"
    )

    assert result == "123456"
    password_reset_cases._otp_service.create_reset_state.assert_called_once_with(
        email="test@example.com"
    )


async def test_begin_password_recovery_invalid_captcha(password_reset_cases, mocker):
    """Тест: Провал и выброс CaptchaInvalidException, если капча не пройдена."""
    mocker.patch(
        "src.use_cases.password_reset_cases.verify_turnstile_token", return_value=False
    )
    password_reset_cases._otp_service.create_reset_state = AsyncMock()

    with pytest.raises(CaptchaInvalidException):
        await password_reset_cases.begin_password_recovery(
            captcha_token="invalid_token", email="test@example.com"
        )

    password_reset_cases._otp_service.create_reset_state.assert_not_called()
