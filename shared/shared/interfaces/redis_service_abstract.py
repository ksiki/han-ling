from abc import ABC, abstractmethod

from redis import Redis


class RedisServiceAbstract(ABC):
    def __init__(self, redis_client: Redis):
        """Инициализирует базовый сервис Redis с переданным клиентом.

        Args:
            redis_client: Экземпляр клиента Redis для выполнения операций с хранилищем.
        """
        self.redis = redis_client

    @abstractmethod
    def _make_key(self) -> str:
        """Формирует ключ для сохранения или извлечения данных из Redis.

        Returns:
            str: Сгенерированный строковый ключ.

        Raises:
            NotImplementedError: Если метод не реализован в подклассе.
        """
        raise NotImplementedError
