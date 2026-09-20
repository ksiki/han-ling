from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core.exceptions import CaptchaInvalidException, PasswordOrEmailInvalidException


async def test_login_by_email_success(auth_cases, mock_uow, mocker):
    mocker.patch("src.use_cases.auth_cases.verify_turnstile_token", return_value=True)
    mock_user = MagicMock()
    auth_cases._login_service.authenticate = AsyncMock(return_value=mock_user)
    auth_cases._session_service.create_session = AsyncMock(
        return_value=("access", "refresh")
    )

    result = await auth_cases.login_by_email(
        captcha_token="valid_captcha",
        email="test@example.com",
        password="secure_password",
        ip="192.168.1.1",
        user_agent="Mozilla/5.0",
    )

    assert result == ("access", "refresh")
    auth_cases._login_service.authenticate.assert_called_once_with(
        email="test@example.com", password="secure_password"
    )
    auth_cases._session_service.create_session.assert_called_once_with(
        user=mock_user, ip="192.168.1.1", user_agent="Mozilla/5.0"
    )
    mock_uow.commit.assert_called_once()


async def test_login_by_email_invalid_captcha(auth_cases, mock_uow, mocker):
    mocker.patch("src.use_cases.auth_cases.verify_turnstile_token", return_value=False)

    with pytest.raises(CaptchaInvalidException):
        await auth_cases.login_by_email(
            captcha_token="invalid",
            email="test@example.com",
            password="secure_password",
            ip="192.168.1.1",
            user_agent="Mozilla/5.0",
        )

    mock_uow.commit.assert_not_called()


@pytest.mark.parametrize("invalid_password", ["", "   ", None])
async def test_login_by_email_invalid_password(
    auth_cases, mock_uow, mocker, invalid_password
):
    mocker.patch("src.use_cases.auth_cases.verify_turnstile_token", return_value=True)

    with pytest.raises(PasswordOrEmailInvalidException):
        await auth_cases.login_by_email(
            captcha_token="valid_captcha",
            email="test@example.com",
            password=invalid_password,
            ip="192.168.1.1",
            user_agent="Mozilla/5.0",
        )

    mock_uow.commit.assert_not_called()


async def test_login_by_email_auth_failure(auth_cases, mock_uow, mocker):
    mocker.patch("src.use_cases.auth_cases.verify_turnstile_token", return_value=True)
    auth_cases._login_service.authenticate = AsyncMock(
        side_effect=PasswordOrEmailInvalidException
    )

    with pytest.raises(PasswordOrEmailInvalidException):
        await auth_cases.login_by_email(
            captcha_token="valid_captcha",
            email="test@example.com",
            password="wrong_password",
            ip="192.168.1.1",
            user_agent="Mozilla/5.0",
        )

    mock_uow.commit.assert_not_called()
