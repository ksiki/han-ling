from shared.db.models import ReprMexin, TimestampMixin
from sqlalchemy.orm import DeclarativeBase


class BaseORM(DeclarativeBase, TimestampMixin, ReprMexin):
    pass
