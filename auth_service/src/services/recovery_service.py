from src.core.security import get_password_hash
from src.db import UnitOfWork
from src.models import UserORM


class RecoveryService:
    def __init__(self, uow: UnitOfWork) -> None:
        """Инициализирует сервис восстановления доступа.

        Args:
            uow: Экземпляр Unit of Work для управления транзакциями и доступа к репозиториям.
        """
        self._uow = uow

    async def change_password_by_email(self, email: str, new_password: str) -> UserORM:
        """Обновляет пароль пользователя по его адресу электронной почты.

        Args:
            email: Адрес электронной почты пользователя.
            new_password: Новый пароль в открытом виде для хэширования и сохранения.

        Returns:
            UserORM: Экземпляр пользователя с обновленным хэшем пароля.

        Raises:
            UserNotFoundException: Если пользователь с указанным адресом электронной почты не найден.
        """
        user = await self._uow.user.get_by_email(email=email)

        new_password_hash = get_password_hash(password=new_password)
        user.password_hash = new_password_hash

        return user
