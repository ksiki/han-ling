import asyncio
import logging

from redis.asyncio import Redis
from redis.exceptions import RedisError
from shared.interfaces import BlacklistedTokenMeta, ITokenBlacklistService

logger = logging.getLogger(__name__)


class TokenBlacklistService(ITokenBlacklistService):
    NAMESPACE: str = "blacklist:token:"

    def __init__(self, redis_client: Redis):
        super().__init__()
        self.redis = redis_client

    def _make_key(self, jti: str) -> str:
        return f"{self.NAMESPACE}{jti}"

    async def add_to_blacklist(
        self, jti: str, meta: BlacklistedTokenMeta, expires_in: int
    ) -> None:
        key = self._make_key(jti=jti)
        meta_value = meta.model_dump_json()

        try:
            await asyncio.wait_for(
                self.redis.setex(name=key, time=expires_in, value=meta_value),
                timeout=0.2,
            )
        except (TimeoutError, RedisError) as e:
            logger.error(f"Failed to add token {jti} to blacklist: {e}")

    async def is_blacklist(self, jti: str) -> bool:
        key = self._make_key(jti=jti)

        try:
            result = await asyncio.wait_for(
                self.redis.exists(key),
                timeout=0.1,
            )
            return result > 0
        except (TimeoutError, RedisError) as e:
            logger.error(f"Redis is down, cannot check blacklist for {jti}: {e}")
            return False
