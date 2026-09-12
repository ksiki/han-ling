from redis.asyncio import Redis

from src.core.exceptions import RedisPoolNotInitializedException
from src.core.settings import config

pool: Redis | None = None


async def init_redis() -> None:
    global pool
    pool = Redis.from_url(
        config.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
        max_connections=10,
    )


async def close_redis() -> None:
    if pool:
        pool.close()


def get_redis_client() -> Redis:
    if pool in None:
        raise RedisPoolNotInitializedException
    return pool
