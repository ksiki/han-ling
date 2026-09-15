from src.core.exceptions import UserAlreadyExistsException
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
        user = await self._uow.user.get_by_email(email=email)
        if user:
            raise UserAlreadyExistsException

    async def create_user(self, email: str, password_hash: str) -> UserORM:
        """Создает нового пользователя и сохраняет его в базе данных.

        Args:
            email: Адрес электронной почты пользователя.
            password_hash: Хэш пароля пользователя.

        Returns:
            uuid.UUID: Уникальный идентификатор созданного пользователя.
        """
        user = UserORM(email=email, password_hash=password_hash)
        return await self._uow.user.add(user)
