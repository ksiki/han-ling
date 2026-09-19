from unittest.mock import MagicMock

import pytest

# Замени пути на реальные
from src.core.exceptions import UserNotFoundException
from src.models import UserORM


async def test_change_password_by_email_success(recovery_service, mock_uow, mocker):
    """Тест: Успешное обновление пароля пользователя."""
    email = "test@example.com"
    new_password = "new_secure_password"
    expected_hash = "hashed_new_secure_password"

    mock_user = MagicMock(spec=UserORM)
    mock_user.password_hash = "old_hash"

    mock_uow.user.get_by_email.return_value = mock_user

    mock_hash = mocker.patch(
        "src.services.recovery_service.get_password_hash", return_value=expected_hash
    )

    result = await recovery_service.change_password_by_email(
        email=email, new_password=new_password
    )

    assert result == mock_user
    assert result.password_hash == expected_hash

    mock_uow.user.get_by_email.assert_called_once_with(email=email)
    mock_hash.assert_called_once_with(password=new_password)


async def test_change_password_by_email_user_not_found(
    recovery_service, mock_uow, mocker
):
    """Тест: Исключение UserNotFoundException, если пользователь не найден."""
    email = "notfound@example.com"
    new_password = "any_password"

    mock_uow.user.get_by_email.side_effect = UserNotFoundException()

    mock_hash = mocker.patch("src.services.recovery_service.get_password_hash")

    with pytest.raises(UserNotFoundException):
        await recovery_service.change_password_by_email(
            email=email, new_password=new_password
        )

    mock_uow.user.get_by_email.assert_called_once_with(email=email)
    mock_hash.assert_not_called()
