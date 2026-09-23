import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared.deploy import setup_logging, setup_telemetry
from shared.http_handlers import init_exception_handlers

from src.api.system import router as system_router
from src.api.v1.router import router as v1_router
from src.core.http import http_client
from src.core.settings import config
from src.db import async_engine
from src.redis.client import close_redis, init_redis

log_level = logging.INFO if config.DEBUG else logging.WARNING
setup_logging(log_level)
logger = structlog.get_logger(__name__)


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
    logger.info(f"Запуск миксросевиса {config.PRODUCT_NAME} Auth...")
    await init_redis()
    yield
    await http_client.aclose()
    await async_engine.dispose()
    await close_redis()
    logger.info(f"Микросервис {config.PRODUCT_NAME} Auth выключен")


app = FastAPI(
    title=f"{config.PRODUCT_NAME} Auth",
    description="Микросервис авторизации, регистрации и аутентификации",
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

setup_telemetry(
    app=app,
    sentry_dsn=config.SENTRY_DSN,
    sentry_traces_sample_rate=config.SENTRY_TRACES_SAMPLE_RATE,
    environment=config.ENVIRONMENT,
    otlp_endpoint=config.OTLP_ENDPOINT,
    product_name=config.PRODUCT_NAME,
    async_engine=async_engine,
)

init_exception_handlers(app=app)

app.include_router(system_router)
app.include_router(v1_router)
