from abc import ABC, abstractmethod
from typing import Self


class UnitOfWorkAbstract(ABC):
    """Абстрактный класс Unit of Work (Паттерн Единица Работы)."""

    async def __aenter__(self) -> Self:
        """Входит в асинхронный контекстный менеджер.

        Returns:
            Self: Экземпляр контекстного менеджера Unit of Work.
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Выходит из асинхронного контекстного менеджера с автоматическим откатом при ошибке.

        Args:
            exc_type: Тип возникшего исключения или None, если исключений не было.
            exc_val: Экземпляр возникшего исключения или None.
            exc_tb: Объект трассировки стека (traceback) или None.
        """
        if exc_type is not None:
            await self.rollback()

    @abstractmethod
    async def commit(self) -> None:
        """Фиксирует все изменения текущей транзакции.

        Raises:
            NotImplementedError: Если метод не реализован в подклассе.
        """
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        """Откатывает все изменения текущей транзакции.

        Raises:
            NotImplementedError: Если метод не реализован в подклассе.
        """
        raise NotImplementedError

    @abstractmethod
    async def flush(self) -> None:
        """Сбрасывает накопившиеся изменения в базу данных без фиксации транзакции.

        Raises:
            NotImplementedError: Если метод не реализован в подклассе.
        """
        raise NotImplementedError
