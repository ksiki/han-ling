from typing import Self

from shared.interfaces import UnitOfWorkAbstract
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.db.repositories import UserRepository
from src.models import UserORM


class UnitOfWork(UnitOfWorkAbstract):
    """
    Реализация UnitOfWork

    Репозитории:
        - user: UserRepository
    """

    def __init__(self, session_maker: async_sessionmaker[AsyncSession]) -> None:
        super().__init__()
        self._session_factory = session_maker

    async def __aenter__(self) -> Self:
        self._session = self._session_factory()

        self.user = UserRepository(session=self._session, model_cls=UserORM)
        return await super().__aenter__()

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await super().__aexit__(exc_type, exc, tb)
        await self._session.aclose()

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
