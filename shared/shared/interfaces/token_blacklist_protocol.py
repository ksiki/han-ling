from typing import Protocol

from pydantic import BaseModel


class BlacklistedTokenMeta(BaseModel):
    """
    Базовый класс для TokenBlacklistService

    revoked_at: время добавления в черный список
    reason: причина
    """

    revoked_at: str
    reason: str


class ITokenBlacklistService(Protocol):
    """
    Интерфейс для сервиса черного списка токенов

    Реализовывает:
        - add_to_blacklist: мотод добавления токена в черный список
        - is_blacklist: проверка на наличие токена в черном списке
    """

    async def add_to_blacklist(
        self, token: str, meta: BlacklistedTokenMeta, expires_in: int
    ) -> None:
        """
        Метод добавляет токен в черный список

        Принимает:
            - токен: str
            - мета данные: BlacklistedTokenMeta
            - время жизни токена в черном списке (секунды): int
        """
        return NotImplementedError

    async def is_blacklist(self, token: str) -> bool:
        """
        Метод проверяет находится ли токен в черном списке

        Принимает:
            - токен: str

        Возвращает:
            - true если токен в черном списке: bool
            - false если токена нет черном списке: bool
        """
        ...
        return NotImplementedError
