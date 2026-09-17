import asyncio
import logging

from fastapi import APIRouter, Response, status
from sqlalchemy import text

from src.core.settings import config
from src.db import async_engine
from src.redis.client import get_redis_client

logger = logging.getLogger(__name__)


router = APIRouter(tags=["System"])


@router.get("/health")
async def health_check() -> dict:
    """
    Liveness probe. Указывает, что процесс запущен и обрабатывает HTTP-запросы.
    """
    return {
        "status": "ok",
        "debug": config.DEBUG,
    }


@router.get("/ready")
async def readiness_check(response: Response) -> dict:
    """
    Readiness probe. Проверяет доступность критических зависимостей (Postgres, Redis).
    """

    async def check_postgres() -> bool:
        try:
            async with async_engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Readiness check failed for Postgres: {e}")
            return False

    async def check_redis() -> bool:
        try:
            redis_client = get_redis_client()
            await redis_client.ping()
            return True
        except Exception as e:
            logger.error(f"Readiness check failed for Redis: {e}")
            return False

    try:
        results = await asyncio.wait_for(
            asyncio.gather(check_postgres(), check_redis()), timeout=2.0
        )
        pg_ok, redis_ok = results
    except TimeoutError:
        logger.error("Readiness check timed out")
        pg_ok, redis_ok = False, False
    except Exception as e:
        logger.error(f"Readiness check unexpected error: {e}")
        pg_ok, redis_ok = False, False

    response_data = {
        "status": "ready" if pg_ok and redis_ok else "not_ready",
        "services": {
            "postgres": "ok" if pg_ok else "unreachable",
            "redis": "ok" if redis_ok else "unreachable",
        },
    }

    if not (pg_ok and redis_ok):
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return response_data
