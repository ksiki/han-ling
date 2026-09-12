import datetime

from sqlalchemy import DateTime, text
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    """
    Миксин для добавления временных меток во все модели
    """

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        server_default=text("TIMEZONE('utc', now())"),
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        onupdate=lambda: datetime.datetime.now(datetime.timezone.utc),
        server_default=text("TIMEZONE('utc', now())"),
    )


class ReprMexin:
    """
    Миксин для удобного строкового представления
    """

    repr_cols_num = 3
    repr_cols = ()

    def __repr__(self) -> str:
        columns = []
        for i, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or i < self.repr_cols_num:
                columns.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(columns)}>"
