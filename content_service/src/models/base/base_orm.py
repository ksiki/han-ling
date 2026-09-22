from typing import Any, ClassVar

from shared.db.models import ReprMixin
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import DeclarativeBase

from src.models.types.enums import (
    BookCharacterRoleEnum,
    BookCreatorRoleEnum,
    BookProcessingStatusEnum,
    BookPublicationStatusEnum,
    UserRoleEnum,
)

user_rote_enum_type = ENUM(
    UserRoleEnum,
    name="user_role_enum",
    values_callable=lambda obj: [e.value for e in obj],
)

book_character_role_enum_type = ENUM(
    BookCharacterRoleEnum,
    name="book_character_role_enum",
    values_callable=lambda obj: [e.value for e in obj],
)

book_creator_role_enum_type = ENUM(
    BookCreatorRoleEnum,
    name="book_creator_role_enum",
    values_callable=lambda obj: [e.value for e in obj],
)

book_processing_status_enum_type = ENUM(
    BookProcessingStatusEnum,
    name="book_processing_status_enum",
    values_callable=lambda obj: [e.value for e in obj],
)

book_publication_status_enum_type = ENUM(
    BookPublicationStatusEnum,
    name="book_publication_status_enum",
    values_callable=lambda obj: [e.value for e in obj],
)


class BaseORM(DeclarativeBase, ReprMixin):
    type_annotation_map: ClassVar[dict[Any, Any]] = {
        UserRoleEnum: user_rote_enum_type,
        BookCharacterRoleEnum: book_character_role_enum_type,
        BookCreatorRoleEnum: book_creator_role_enum_type,
        BookProcessingStatusEnum: book_processing_status_enum_type,
        BookPublicationStatusEnum: book_publication_status_enum_type,
    }
