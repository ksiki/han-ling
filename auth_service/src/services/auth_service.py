from src.core.exceptions import PasswordOrEmailInvalidException, UserNotFoundException
from src.core.security import verify_password
from src.db import UnitOfWork
from src.models import UserORM


class AuthService:
    def __init__(self, uow: UnitOfWork) -> None:
        """Инициализирует сервис аутентификации.

        Args:
            uow: Экземпляр Unit of Work для доступа к репозиториям и управлению транзакциями.
        """
        self._uow = uow

    async def authenticate(self, email: str, password: str | None) -> UserORM:
        """Аутентифицирует пользователя по адресу электронной почты и паролю.

        Args:
            email: Email адрес пользователя.
            password: Пароль пользователя в открытом виде для сверки (или None, если проверка пароля пропускается).

        Returns:
            UserORM: Экземпляр успешно аутентифицированного пользователя.

        Raises:
            PasswordOrEmailInvalidException: Если пользователь с указанным email не найден или передан неверный пароль.
        """
        try:
            user = await self._uow.user.get_by_email(email=email)
        except UserNotFoundException:
            raise PasswordOrEmailInvalidException

        if password is None:
            return user

        if user.password_hash and not verify_password(
            plain_password=password, hashed_password=user.password_hash
        ):
            raise PasswordOrEmailInvalidException
        return user
