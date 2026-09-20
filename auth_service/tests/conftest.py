import asyncio

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.api.dependencies import _get_uow
from src.core.settings import config
from src.db.unit_of_work import UnitOfWork
from src.main import app


@pytest.fixture(scope="session", autouse=True)
def patch_database_url():
    """
    Глобально подменяет настройки БД на тестовые.
    Обходит ограничение Pydantic frozen=True с помощью базового object.__setattr__.
    """
    test_db_name = "test_postgres"

    original_host = config.POSTGRES_HOST
    original_db = config.POSTGRES_DB

    object.__setattr__(config, "POSTGRES_HOST", "localhost")
    object.__setattr__(config, "POSTGRES_DB", test_db_name)

    yield str(config.DATABASE_URL)

    object.__setattr__(config, "POSTGRES_HOST", original_host)
    object.__setattr__(config, "POSTGRES_DB", original_db)


async def create_test_database_if_not_exists() -> None:
    """Создает физическую тестовую БД, если она не существует."""
    base_url = str(config.DATABASE_URL).replace(config.POSTGRES_DB, "postgres")

    engine = create_async_engine(base_url, isolation_level="AUTOCOMMIT")

    async with engine.connect() as conn:
        result = await conn.execute(
            text(f"SELECT 1 FROM pg_database WHERE datname = '{config.POSTGRES_DB}'")
        )
        exists = result.scalar()

        if not exists:
            await conn.execute(text(f"CREATE DATABASE {config.POSTGRES_DB}"))

    await engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def prepare_database(patch_database_url):
    """
    Синхронная фикстура уровня сессии.
    Указываем patch_database_url в аргументах, чтобы гарантировать, что мок применится до старта.
    """
    asyncio.run(create_test_database_if_not_exists())

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
    finally:
        loop.close()
        asyncio.set_event_loop(None)

    yield


@pytest_asyncio.fixture
async def db_session_maker():
    """
    Создает изолированную транзакцию для каждого теста.
    """
    test_engine = create_async_engine(config.DATABASE_URL, poolclass=NullPool)

    async with test_engine.connect() as conn:
        transaction = await conn.begin()

        session_maker = async_sessionmaker(
            bind=conn, class_=AsyncSession, expire_on_commit=False, autoflush=False
        )

        yield session_maker

        await transaction.rollback()

    await test_engine.dispose()


@pytest_asyncio.fixture
async def test_uow(db_session_maker):
    """Подменяет Unit of Work, внедряя в него транзакционную сессию."""
    uow = UnitOfWork(session_maker=db_session_maker)
    async with uow:
        yield uow


@pytest_asyncio.fixture
async def client(test_uow):
    """
    HTTP клиент для тестов.
    Подменяет реальную зависимость `_get_uow` на тестовую.
    """
    app.dependency_overrides[_get_uow] = lambda: test_uow

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
