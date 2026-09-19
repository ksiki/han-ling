from unittest.mock import MagicMock

import pytest

from src.core.exceptions import UserAlreadyExistsException, UserNotFoundException
from src.models import UserORM


async def test_check_email_success(registration_service, mock_uow):
    """Тест: Успех (email свободен).
    Репозиторий не находит пользователя и выбрасывает UserNotFoundException.
    Метод должен подавить ошибку и завершиться без возврата (None).
    """
    email = "new_user@example.com"

    mock_uow.user.get_by_email.side_effect = UserNotFoundException()

    result = await registration_service.check_email(email=email)

    assert result is None
    mock_uow.user.get_by_email.assert_called_once_with(email=email)


async def test_check_email_already_exists(registration_service, mock_uow):
    """Тест: Провал (email занят).
    Репозиторий возвращает пользователя, метод выбрасывает UserAlreadyExistsException.
    """
    email = "existing_user@example.com"

    mock_user = MagicMock(spec=UserORM)
    mock_uow.user.get_by_email.return_value = mock_user

    mock_uow.user.get_by_email.side_effect = None

    with pytest.raises(UserAlreadyExistsException):
        await registration_service.check_email(email=email)

    mock_uow.user.get_by_email.assert_called_once_with(email=email)
