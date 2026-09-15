from shared.db import SQLAclchemyRepository

from src.models import UserProviderORM


class UserProviderRepository(SQLAclchemyRepository[UserProviderORM]):
    def __init__(self, session):
        super().__init__(session, model_cls=UserProviderORM)
