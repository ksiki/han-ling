from abc import ABC

from redis.asyncio import Redis


class RedisServiceAbstract(ABC):
    def __init__(self, redis_client: Redis):
        """Инициализирует базовый сервис Redis с переданным клиентом.

        Args:
            redis_client: Экземпляр клиента Redis для выполнения операций с хранилищем.
        """
        self._redis = redis_client
