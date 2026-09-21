import enum


class UserRoleEnum(enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class BookCreatorRoleEnum(enum.Enum):
    AUTHOR = "AUTHOR"
    EDITOR = "EDITOR"
    ILLUSTRATOR = "ILLUSTRATOR"
    DESIGNER = "DESIGNER"
    PUBLISHER = "PUBLISHER"


class BookCharacterRoleEnum(enum.Enum):
    MAIN = "MAIN"
    SECONDARY = "SECONDARY"
    CAMEO = "CAMEO"
