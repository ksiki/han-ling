from shared.db.sqlalchemy_repository import SQLAclchemyRepository

from .outbox_orm import OutboxMessageORM


class OutboxMessageRepository(SQLAclchemyRepository[OutboxMessageORM]):
    def __init__(self, session) -> None:
        """Инициализирует репозиторий пользователей с моделью OutboxMessageORM.

        Args:
            session: Асинхронная сессия SQLAlchemy для взаимодействия с базой данных.
        """
        super().__init__(session, model_cls=OutboxMessageORM)
