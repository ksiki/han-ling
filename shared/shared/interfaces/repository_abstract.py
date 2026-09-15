from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class RepositoryAbstract(ABC, Generic[T]):
    @abstractmethod
    async def add(self, entity: T) -> T:
        """Добавляет новую сущность в репозиторий.

        Args:
            entity: Добавляемый объект сущности.

        Returns:
            T: Добавленная сущность с обновленным состоянием.

        Raises:
            NotImplementedError: Если метод не реализован в подклассе.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_or_none(self, **kwargs: Any) -> T | None:
        """Получает одну сущность по заданным критериям фильтрации.

        Args:
            **kwargs: Именованные аргументы с полями и значениями для фильтрации.

        Returns:
            T | None: Найденная сущность или None, если запись не найдена.

        Raises:
            NotImplementedError: Если метод не реализован в подклассе.
        """
        raise NotImplementedError
