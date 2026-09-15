from typing import Self

from shared.interfaces import UnitOfWorkAbstract
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.db.repositories import (
    UserProviderRepository,
    UserRepository,
    UserSessionRepository,
)


class UnitOfWork(UnitOfWorkAbstract):
    """
    Args:
        user: UserRepository
        user_session: UserSessionRepository
        user_provider: UserProviderRepository
    """

    def __init__(self, session_maker: async_sessionmaker[AsyncSession]) -> None:
        """Инициализирует экземпляр Unit of Work с фабрикой асинхронных сессий.

        Args:
            session_maker: Фабрика для создания асинхронных сессий SQLAlchemy.
        """
        super().__init__()
        self._session_factory = session_maker

    async def __aenter__(self) -> Self:
        """Создает новую асинхронную сессию и инициализирует репозитории.

        Returns:
            Self: Экземпляр Unit of Work с активной сессией и инициализированными репозиториями.
        """
        self._session = self._session_factory()

        self.user = UserRepository(session=self._session)
        self.user_session = UserSessionRepository(session=self._session)
        self.user_provider = UserProviderRepository(session=self._session)

        return await super().__aenter__()

    async def __aexit__(self, exc_type, exc, tb) -> None:
        """Завершает контекстный менеджер, выполняя базовые действия и закрывая сессию.

        Args:
            exc_type: Тип возникшего исключения или None, если исключений не было.
            exc: Экземпляр возникшего исключения или None.
            tb: Объект трассировки стека (traceback) или None.
        """
        await super().__aexit__(exc_type, exc, tb)
        await self._session.aclose()

    async def commit(self) -> None:
        """Фиксирует все изменения текущей сессии базы данных."""
        await self._session.commit()

    async def rollback(self) -> None:
        """Откатывает все изменения текущей сессии базы данных."""
        await self._session.rollback()

    async def flush(self) -> None:
        """Сбрасывает накопившиеся изменения сессии в базу данных без фиксации транзакции."""
        await self._session.flush()
