from shared.db.models import ReprMixin, TimestampMixin
from sqlalchemy.orm import DeclarativeBase


class BaseORM(DeclarativeBase, TimestampMixin, ReprMixin):
    pass
