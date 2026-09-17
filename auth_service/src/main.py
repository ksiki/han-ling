import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from shared.http_handlers import init_exception_handlers
from sqlalchemy import text

from src.api.v1.router import router as v1_router
from src.core.http import http_client
from src.core.settings import config
from src.db import async_engine
from src.redis.client import close_redis, get_redis_client, init_redis

log_level = logging.INFO if config.DEBUG else logging.WARNING
logging.basicConfig(
    level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Управляет жизненным циклом приложения: инициализацией и корректным завершением ресурсов.

    Инициализирует подключение к Redis при старте сервиса.
    При остановке закрывает HTTP-клиент, пул соединений SQLAlchemy и клиент Redis.

    Args:
        app: Экземпляр приложения FastAPI.

    Yields:
        None: Передает управление работающему приложению.
    """
    logger.info("Запуск миксросевиса HanLing Auth...")
    await init_redis()
    yield
    await http_client.aclose()
    await async_engine.dispose()
    await close_redis()
    logger.info("Микросервис HanLing Auth выключен")


app = FastAPI(
    title="HanLing Auth",
    description="Микросервис авторизации, регистрации и аутентификации для HanLing",
    version="1.0.0",
    root_path="/auth",
    docs_url="/api/docs" if config.DEBUG else None,
    openapi_url="/api/openapi.json" if config.DEBUG else None,
    redoc_url="/api/redoc" if config.DEBUG else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.FRONTEND_URLS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_exception_handlers(app=app)

app.include_router(v1_router)


@app.get("/health", tags=["System"])
async def health_check() -> dict:
    """
    Liveness probe. Указывает, что процесс запущен и обрабатывает HTTP-запросы.
    """
    return {
        "status": "ok",
        "debug": config.DEBUG,
    }


@app.get("/ready", tags=["System"])
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
