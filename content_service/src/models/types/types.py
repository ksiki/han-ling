from typing import Annotated

from sqlalchemy.orm import mapped_column

from .enums import (
    BookCharacterRoleEnum,
    BookCreatorRoleEnum,
    BookProcessingStatusEnum,
    BookPublicationStatusEnum,
    LearningStatusEnum,
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

learning_status = Annotated[
    LearningStatusEnum,
    mapped_column(
        server_default=LearningStatusEnum.NEW, default=LearningStatusEnum.NEW
    ),
]

user_role = Annotated[
    UserRoleEnum,
    mapped_column(
        server_default=UserRoleEnum.USER.value,
        default=UserRoleEnum.USER,
    ),
]

book_processing_status = Annotated[
    BookProcessingStatusEnum,
    mapped_column(
        server_default=BookProcessingStatusEnum.PENDING.value,
        default=BookProcessingStatusEnum.PENDING,
        comment="Технический статус обработки книги (очередь, обработка, завершено)",
    ),
]

book_publication_status = Annotated[
    BookPublicationStatusEnum,
    mapped_column(
        server_default=BookPublicationStatusEnum.COMING_SOON.value,
        default=BookPublicationStatusEnum.COMING_SOON,
        comment="Статус видимости книги на сайте (черновик, скоро, опубликовано, скрыто)",
    ),
]
