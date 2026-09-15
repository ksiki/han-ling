from shared.db import SQLAclchemyRepository

from src.models import UserORM


class UserRepository(SQLAclchemyRepository[UserORM]):
    def __init__(self, session) -> None:
        """Инициализирует репозиторий пользователей с моделью UserORM.

        Args:
            session: Асинхронная сессия SQLAlchemy для взаимодействия с базой данных.
        """
        super().__init__(session, model_cls=UserORM)

    async def get_by_email(self, email: str) -> UserORM | None:
        """Получает пользователя по адресу электронной почты.

        Args:
            email: Адрес электронной почты для поиска.

        Returns:
            UserORM | None: Экземпляр найденного пользователя или None, если пользователь не найден.
        """
        return await self.get_or_none(email=email)
