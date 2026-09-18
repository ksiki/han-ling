from unittest.mock import MagicMock

import pytest

from src.core.exceptions import PasswordOrEmailInvalidException, UserNotFoundException
from src.models import UserORM


async def test_authenticate_success_with_password(auth_service, mock_uow, mocker):
    """Тест: Успешная аутентификация с правильным паролем."""
    email = "test@example.com"
    password = "correct_password"

    mock_user = MagicMock(spec=UserORM)
    mock_user.password_hash = "hashed_password"
    mock_uow.user.get_by_email.return_value = mock_user

    mock_verify = mocker.patch(
        "src.services.auth_service.verify_password", return_value=True
    )

    result = await auth_service.authenticate(email=email, password=password)

    assert result == mock_user
    mock_uow.user.get_by_email.assert_called_once_with(email=email)
    mock_verify.assert_called_once_with(
        plain_password=password, hashed_password=mock_user.password_hash
    )


async def test_authenticate_success_without_password(auth_service, mock_uow, mocker):
    """Тест: Успешная аутентификация, если password=None (проверка пароля пропускается)."""
    email = "test@example.com"

    mock_user = MagicMock(spec=UserORM)
    mock_uow.user.get_by_email.return_value = mock_user

    mock_verify = mocker.patch("src.services.auth_service.verify_password")

    result = await auth_service.authenticate(email=email, password=None)

    assert result == mock_user
    mock_uow.user.get_by_email.assert_called_once_with(email=email)
    mock_verify.assert_not_called()


async def test_authenticate_user_not_found(auth_service, mock_uow):
    """Тест: Ошибка PasswordOrEmailInvalidException, если пользователь не найден."""
    email = "notfound@example.com"
    password = "any_password"

    mock_uow.user.get_by_email.side_effect = UserNotFoundException()

    with pytest.raises(PasswordOrEmailInvalidException):
        await auth_service.authenticate(email=email, password=password)

    mock_uow.user.get_by_email.assert_called_once_with(email=email)


async def test_authenticate_invalid_password(auth_service, mock_uow, mocker):
    """Тест: Ошибка PasswordOrEmailInvalidException, если пароль неверный."""
    email = "test@example.com"
    password = "wrong_password"

    mock_user = MagicMock(spec=UserORM)
    mock_user.password_hash = "hashed_password"
    mock_uow.user.get_by_email.return_value = mock_user

    mock_verify = mocker.patch(
        "src.services.auth_service.verify_password", return_value=False
    )

    with pytest.raises(PasswordOrEmailInvalidException):
        await auth_service.authenticate(email=email, password=password)

    mock_uow.user.get_by_email.assert_called_once_with(email=email)
    mock_verify.assert_called_once_with(
        plain_password=password, hashed_password=mock_user.password_hash
    )
