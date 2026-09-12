from typing import Annotated
from uuid import UUID

from sqlalchemy.orm import mapped_column
from uuid6 import uuid7

uuid_pk = Annotated[UUID, mapped_column(primary_key=True, default=uuid7)]
