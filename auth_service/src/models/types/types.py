from typing import Annotated

from sqlalchemy.orm import mapped_column

from .enums import ProviderEnum, RoleEnum

provider_type = Annotated[
    ProviderEnum,
    mapped_column(
        comment="Тип внешнего OAuth-провайдера аутентификации",
    ),
]

user_role = Annotated[
    RoleEnum,
    mapped_column(
        server_default=RoleEnum.USER.value,
        default=RoleEnum.USER,
        comment="Роль пользователя в системе для разграничения прав доступа",
    ),
]
