from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.interfaces import RepositoryAbstract, T


class SQLAclchemyRepository(RepositoryAbstract[T]):
    def __init__(self, session: AsyncSession, model_cls: type[T]) -> None:
        """Инициализирует экземпляр репозитория с асинхронной сессией и классом модели.

        Args:
            session: Асинхронная сессия SQLAlchemy для взаимодействия с базой данных.
            model_cls: Класс модели SQLAlchemy, с которой работает данный репозиторий.
        """
        super().__init__()
        self._session = session
        self._model_cls = model_cls

    async def add(self, entity: T) -> T:
        """Добавляет экземпляр сущности в сессию базы данных.

        Args:
            entity: Экземпляр модели для сохранения.

        Returns:
            T: Переданный экземпляр сущности, прикрепленный к сессии.
        """
        self._session.add(entity)
        return entity

    async def get_or_none(self, **kwargs: Any) -> T | None:
        """Находит и возвращает одну запись модели по переданным критериям фильтрации.

        Args:
            **kwargs: Именованные параметры, соответствующие колонкам модели для фильтрации.

        Returns:
            T | None: Найденный экземпляр модели или None, если подходящая запись не найдена.
        """
        query = select(self._model_cls).filter_by(**kwargs)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()
