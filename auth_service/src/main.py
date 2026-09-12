import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared.http_handlers import init_exception_handlers

from src.api.v1 import v1_router
from src.core.settings import config
from src.db import async_engine
from src.redis.client import close_redis, init_redis

log_level = logging.INFO if config.DEBUG else logging.WARNING
logging.basicConfig(
    level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Запуск миксросевиса HanLing Auth...")
    await init_redis()
    yield
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


@app.get("/health")
async def health_check() -> dict[str, Any]:
    """
    Ручка для проверки статуса сервиса

    Принимает:
        - Ничего

    Возвращает dict:
        - status: str
        - debug: bool
    """

    return {
        "status": "ok",
        "debug": config.DEBUG,
    }
