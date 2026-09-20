from unittest.mock import AsyncMock

import pytest

from src.core.exceptions import CaptchaInvalidException, UserAlreadyExistsException


async def test_begin_registration_success(registration_cases, mocker):
    """Тест: Успешное начало регистрации с генерацией OTP."""
    registration_cases._registration_service.check_email = AsyncMock()
    mocker.patch(
        "src.use_cases.registration_cases.verify_turnstile_token", return_value=True
    )
    registration_cases._otp_service.create_registration_state = AsyncMock(
        return_value="123456"
    )

    result = await registration_cases.begin_registration(
        captcha_token="valid_token",
        email="test@example.com",
        password="secure_password",
    )

    assert result == "123456"
    registration_cases._registration_service.check_email.assert_called_once_with(
        email="test@example.com"
    )
    registration_cases._otp_service.create_registration_state.assert_called_once_with(
        email="test@example.com", password="secure_password"
    )


async def test_begin_registration_user_exists(registration_cases, mocker):
    """Тест: Провал и выброс UserAlreadyExistsException, если email занят."""
    registration_cases._registration_service.check_email = AsyncMock(
        side_effect=UserAlreadyExistsException
    )
    mock_verify = mocker.patch(
        "src.use_cases.registration_cases.verify_turnstile_token"
    )
    registration_cases._otp_service.create_registration_state = AsyncMock()

    with pytest.raises(UserAlreadyExistsException):
        await registration_cases.begin_registration(
            captcha_token="valid_token",
            email="test@example.com",
            password="secure_password",
        )

    mock_verify.assert_not_called()
    registration_cases._otp_service.create_registration_state.assert_not_called()


async def test_begin_registration_invalid_captcha(registration_cases, mocker):
    """Тест: Провал и выброс CaptchaInvalidException, если капча не пройдена."""
    registration_cases._registration_service.check_email = AsyncMock()
    mocker.patch(
        "src.use_cases.registration_cases.verify_turnstile_token", return_value=False
    )
    registration_cases._otp_service.create_registration_state = AsyncMock()

    with pytest.raises(CaptchaInvalidException):
        await registration_cases.begin_registration(
            captcha_token="invalid_token",
            email="test@example.com",
            password="secure_password",
        )

    registration_cases._registration_service.check_email.assert_called_once_with(
        email="test@example.com"
    )
    registration_cases._otp_service.create_registration_state.assert_not_called()
