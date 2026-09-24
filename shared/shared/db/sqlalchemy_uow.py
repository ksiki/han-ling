from typing import Self

from db import SQLAclchemyRepository
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from shared.interfaces import T, UnitOfWorkAbstract


class SQLAlchemyBaseUnitOfWork(UnitOfWorkAbstract):
    """Базовая реализация UoW для SQLAlchemy, переиспользуемая во всех микросервисах."""

    def __init__(self, session_maker: async_sessionmaker[AsyncSession]) -> None:
        """Инициализирует базовый Unit of Work фабрикой сессий SQLAlchemy.

        Args:
            session_maker: Фабрика для создания асинхронных сессий SQLAlchemy.
        """
        self._session_factory = session_maker
        self._session: AsyncSession | None = None

    async def __aenter__(self) -> Self:
        """Создает новую асинхронную сессию и входит в контекстный менеджер.

        Returns:
            Self: Экземпляр текущего Unit of Work.
        """
        self._session = self._session_factory()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Закрывает сессию, предварительно откатив изменения при возникновении ошибки.

        Args:
            exc_type: Тип возникшего исключения или None.
            exc_val: Экземпляр возникшего исключения или None.
            exc_tb: Объект трассировки стека (traceback) или None.
        """
        await super().__aexit__(exc_type, exc_val, exc_tb)
        if self._session:
            await self._session.aclose()

    def repository(self, model_cls: type[T]) -> SQLAclchemyRepository[T]:
        """Универсальная фабрика для получения CRUD-репозитория любой модели."""
        return SQLAclchemyRepository(self._session, model_cls=model_cls)

    async def commit(self) -> None:
        """Фиксирует текущую транзакцию в базе данных."""
        if self._session:
            await self._session.commit()

    async def rollback(self) -> None:
        """Откатывает текущую транзакцию."""
        if self._session:
            await self._session.rollback()

    async def flush(self) -> None:
        """Сбрасывает накопившиеся изменения сессии в базу данных без фиксации транзакции."""
        if self._session:
            await self._session.flush()
