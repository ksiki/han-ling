import datetime
from typing import Annotated
from uuid import UUID

from sqlalchemy import DateTime, text
from sqlalchemy.orm import mapped_column
from uuid6 import uuid7

uuid_pk = Annotated[UUID, mapped_column(primary_key=True, default=uuid7)]

created_at_type = Annotated[
    datetime.datetime,
    mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
        server_default=text("TIMEZONE('utc', now())"),
    ),
]
