import os

os.environ["POSTGRES_HOST"] = "localhost"
os.environ["POSTGRES_DB"] = "test_auth_service_db"
os.environ["POSTGRES_PORT"] = "5432"

os.environ["REDIS_HOST"] = "localhost"
os.environ["REDIS_DB"] = "1"

from src.core.settings import config  # noqa
