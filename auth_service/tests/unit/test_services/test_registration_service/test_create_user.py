import pytest

# Замени пути на реальные
from src.models import UserORM


async def test_create_user_success_with_password(registration_service, mock_uow):
    """Тест: Успешное создание пользователя с паролем, добавление в UoW и сброс сессии."""
    email = "new@example.com"
    password_hash = "hashed_secret"

    result = await registration_service.create_user(
        email=email, password_hash=password_hash
    )

    assert isinstance(result, UserORM)
    assert result.email == email
    assert result.password_hash == password_hash

    mock_uow.user.add.assert_called_once_with(result)
    mock_uow.flush.assert_called_once()


async def test_create_user_success_without_password(registration_service, mock_uow):
    """Тест: Успешное создание пользователя без пароля (например, OAuth регистрация)."""
    email = "oauth@example.com"

    result = await registration_service.create_user(email=email, password_hash=None)

    assert isinstance(result, UserORM)
    assert result.email == email
    assert result.password_hash is None

    mock_uow.user.add.assert_called_once_with(result)
    mock_uow.flush.assert_called_once()


async def test_create_user_db_error(registration_service, mock_uow):
    """Тест: Провал при ошибке на уровне БД (например, IntegrityError из-за дубля email)."""
    email = "duplicate@example.com"

    mock_error = Exception("Database Integrity Error")
    mock_uow.user.add.side_effect = mock_error

    with pytest.raises(Exception) as exc_info:
        await registration_service.create_user(email=email, password_hash="hash")

    assert str(exc_info.value) == "Database Integrity Error"

    mock_uow.user.add.assert_called_once()
    mock_uow.flush.assert_not_called()
