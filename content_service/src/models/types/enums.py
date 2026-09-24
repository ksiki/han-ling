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


class BookProcessingStatusEnum(enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class BookPublicationStatusEnum(enum.Enum):
    DRAFT = "DRAFT"
    COMING_SOON = "COMING_SOON"
    PUBLISHED = "PUBLISHED"
    HIDDEN = "HIDDEN"


class LearningStatusEnum(enum.Enum):
    NEW = "NEW"
    LEARNING = "LEARNING"
    REVIEWING = "REVIEWING"
    MASTERED = "MASTERED"
