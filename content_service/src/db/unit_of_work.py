from typing import Self

from shared.db import SQLAlchemyBaseUnitOfWork
from shared.db.outbox import OutboxMessageRepository
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class UnitOfWork(SQLAlchemyBaseUnitOfWork):
    """Реализация Unit of Work для микросервиса с инициализацией специфичных репозиториев.

    Args:
        outbox: Репозиторий для работы с событиями.
    """

    def __init__(self, session_maker: async_sessionmaker[AsyncSession]) -> None:
        """Инициализирует Unit of Work фабрикой сессий и определяет поля репозиториев.

        Args:
            session_maker: Фабрика для создания асинхронных сессий SQLAlchemy.
        """
        super().__init__(session_maker)

        self.outbox: OutboxMessageRepository

    async def __aenter__(self) -> Self:
        """Создает новую асинхронную сессию и инициализирует репозитории.

        Returns:
            Self: Экземпляр Unit of Work с активной сессией и инициализированными репозиториями.
        """
        await super().__aenter__()

        self.outbox = OutboxMessageRepository(session=self._session)

        return self
