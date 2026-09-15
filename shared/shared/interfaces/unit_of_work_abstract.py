from abc import ABC, abstractmethod
from typing import Self


class UnitOfWorkAbstract(ABC):
    async def __aenter__(self) -> Self:
        """Входит в асинхронный контекстный менеджер.

        Returns:
            Self: Экземпляр контекстного менеджера Unit of Work.
        """
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        """Выходит из асинхронного контекстного менеджера с автоматическим откатом.

        Args:
            exc_type: Тип возникшего исключения или None, если исключений не было.
            exc: Экземпляр возникшего исключения или None.
            tb: Объект трассировки стека (traceback) или None.
        """
        await self.rollback()

    @abstractmethod
    async def commit(self) -> None:
        """Фиксирует текущую транзакцию и сохраняет все изменения в хранилище.

        Raises:
            NotImplementedError: Если метод не реализован в подклассе.
        """
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        """Откатывает текущую транзакцию и отменяет несохраненные изменения.

        Raises:
            NotImplementedError: Если метод не реализован в подклассе.
        """
        raise NotImplementedError

    @abstractmethod
    async def flush(self) -> None:
        """Сбрасывает накопившиеся изменения сессии в базу данных без фиксации транзакции.

        Raises:
            NotImplementedError: Если метод не реализован в подклассе.
        """
        raise NotImplementedError
