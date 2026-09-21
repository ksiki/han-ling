from typing import Self

from shared.db import SQLAlchemyBaseUnitOfWork
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.db.repositories import (
    UserProviderRepository,
    UserRepository,
    UserSessionRepository,
)


class UnitOfWork(SQLAlchemyBaseUnitOfWork):
    """Реализация Unit of Work для микросервиса с инициализацией специфичных репозиториев.

    Args:
        user: Репозиторий для работы с сущностями пользователей.
        user_session: Репозиторий для работы с сессиями пользователей.
        user_provider: Репозиторий для работы с внешними OAuth-провайдерами.
    """

    def __init__(self, session_maker: async_sessionmaker[AsyncSession]) -> None:
        """Инициализирует Unit of Work фабрикой сессий и определяет поля репозиториев.

        Args:
            session_maker: Фабрика для создания асинхронных сессий SQLAlchemy.
        """
        super().__init__(session_maker)

        self.user: UserRepository
        self.user_session: UserSessionRepository
        self.user_provider: UserProviderRepository

    async def __aenter__(self) -> Self:
        """Создает новую асинхронную сессию и инициализирует репозитории.

        Returns:
            Self: Экземпляр Unit of Work с активной сессией и инициализированными репозиториями.
        """
        await super().__aenter__()

        self.user = UserRepository(session=self._session)
        self.user_session = UserSessionRepository(session=self._session)
        self.user_provider = UserProviderRepository(session=self._session)

        return self
