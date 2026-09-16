from src.core.exceptions import UserAlreadyExistsException, UserNotFoundException
from src.db import UnitOfWork
from src.models import UserORM


class RegistrationService:
    def __init__(self, uow: UnitOfWork) -> None:
        """Инициализирует сервис регистрации пользователей.

        Args:
            uow: Экземпляр Unit of Work для управления транзакциями и доступа к репозиториям.
        """
        self._uow = uow

    async def check_email(self, email: str) -> None:
        """Проверяет доступность адреса электронной почты для регистрации.

        Args:
            email: Проверяемый адрес электронной почты.

        Raises:
            UserAlreadyExistsException: Если пользователь с таким адресом уже зарегистрирован.
        """
        try:
            await self._uow.user.get_by_email(email=email)
            raise UserAlreadyExistsException
        except UserNotFoundException:
            pass

    async def create_user(self, email: str, password_hash: str | None) -> UserORM:
        """Создает нового пользователя и сохраняет его в базе данных.

        Args:
            email: Адрес электронной почты пользователя.
            password_hash: Хэш пароля пользователя (может быть None).

        Returns:
            uuid.UUID: Уникальный идентификатор созданного пользователя.
        """
        user = UserORM(email=email, password_hash=password_hash)
        await self._uow.user.add(user)
        await self._uow.flush()
        return user
