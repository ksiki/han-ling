from typing import Any, ClassVar

from shared.db.models import ReprMixin, TimestampMixin
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import DeclarativeBase

from src.models.types.enums import ProviderEnum, RoleEnum

provider_enum_type = ENUM(
    ProviderEnum,
    name="provider_enum",
    values_callable=lambda obj: [e.value for e in obj],
)

role_enum_type = ENUM(
    RoleEnum,
    name="role_enum",
    values_callable=lambda obj: [e.value for e in obj],
)


class BaseORM(DeclarativeBase, TimestampMixin, ReprMixin):
    type_annotation_map: ClassVar[dict[Any, Any]] = {
        ProviderEnum: provider_enum_type,
        RoleEnum: role_enum_type,
    }
