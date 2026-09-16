from shared.db import SQLAclchemyRepository

from src.core.exceptions import UserNotFoundException
from src.models import UserORM


class UserRepository(SQLAclchemyRepository[UserORM]):
    def __init__(self, session) -> None:
        """Инициализирует репозиторий пользователей с моделью UserORM.

        Args:
            session: Асинхронная сессия SQLAlchemy для взаимодействия с базой данных.
        """
        super().__init__(session, model_cls=UserORM)

    async def get_by_email(self, email: str) -> UserORM:
        """Получает пользователя по адресу электронной почты с проверкой на существование.

        Args:
            email: Адрес электронной почты пользователя.

        Returns:
            UserORM: Найденный экземпляр пользователя.

        Raises:
            UserNotFoundException: Если пользователь с указанным email не найден.
        """
        user = await self.get_or_none(email=email)
        if not user:
            raise UserNotFoundException

        return user
