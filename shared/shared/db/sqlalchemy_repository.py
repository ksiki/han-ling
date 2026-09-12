from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.interfaces.repository import RepositoryAbstract, T


class SQLAclchemyRepository(RepositoryAbstract[T]):
    """
    Обертка над SQLAlchemy сессией
    """

    def __init__(self, session: AsyncSession, model_cls: type[T]) -> None:
        super().__init__()
        self._session = session
        self._model_cls = model_cls

    async def add(self, entity: T) -> T:
        self._session.add(entity)
        return entity

    async def get(self, id: Any) -> T | None:
        query = select(self._model_cls).filter_by(id=id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_or_none(self, **kwargs: Any) -> T | None:
        query = select(self._model_cls).filter_by(**kwargs)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()
