from typing import Annotated

from sqlalchemy.orm import mapped_column

from .enums import (
    BookCharacterRoleEnum,
    BookCreatorRoleEnum,
    UserRoleEnum,
)

book_character_role = Annotated[
    BookCharacterRoleEnum,
    mapped_column(),
]

book_creator_role = Annotated[
    BookCreatorRoleEnum,
    mapped_column(),
]

user_role = Annotated[
    UserRoleEnum,
    mapped_column(
        server_default=UserRoleEnum.USER.value,
        default=UserRoleEnum.USER,
    ),
]
