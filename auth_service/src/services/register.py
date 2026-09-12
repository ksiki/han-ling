from src.core.exceptions import PasswordsDoNotMatchException, UserAlreadyExistsException
from src.db import UnitOfWork
from src.models import UserORM

from .security import SecurityService


class RegisterService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def _create_new_user(self, email: str, password: str) -> UserORM:
        """
        Метод создания нового пользователя

        Принимает:
            - почта: str
            - пароль: str

        Возвращает:
            - Объект пользователя базы данных: UserORM

        Исключения:
            - если пользователь с такой почтой уже существует: UserAlreadyExistsException
        """

        exists = await self.uow.user.get_or_none(email=email)
        if exists:
            raise UserAlreadyExistsException

        password_hash = SecurityService.get_password_hash(password=password)
        user = UserORM(email=email, password_hash=password_hash)
        await self.uow.user.add(user)

        return user

    async def register(
        self, email: str, password: str, password_replay: str
    ) -> tuple[str]:
        """
        Процесс регистрации пользователя

        Принимает:
            - payload для регистрации: UserRegisterRequest

        Возвращает:
            - access и refresh токены: tuple[str]

        Исключения:
            - если пароль и повтор пароля при регистрации не совпадают: PasswordsDoNotMatchException
            - если пользователь с такой почтой уже существует: UserAlreadyExistsException
        """

        if password != password_replay:
            raise PasswordsDoNotMatchException

        user = await self._create_new_user(
            email=email,
            password=password,
        )
        await self.uow.commit()

        token_payload = self.uow.user.to_token_payload(user=user)
        return SecurityService.create_pair_tokens(data=token_payload)
