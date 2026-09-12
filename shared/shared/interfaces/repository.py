from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class RepositoryAbstract(ABC, Generic[T]):
    """
    Базовый интерфейс репозитория
    """

    @abstractmethod
    async def add(self, entity: T) -> T:
        raise NotImplementedError

    @abstractmethod
    async def get(self, id: Any) -> T | None:
        raise NotImplementedError

    @abstractmethod
    async def get_or_none(self, **kwargs: Any) -> T | None:
        raise NotImplementedError
