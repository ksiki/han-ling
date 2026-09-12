import datetime

from shared.interfaces import BlacklistedTokenMeta
from shared.security import verify_token

from src.core.exceptions import InvalidPasswordOrEmailException
from src.core.settings import config
from src.db import UnitOfWork
from src.models import UserORM
from src.redis import TokenBlacklistService

from .security import SecurityService


class LoginService:
    def __init__(self, uow: UnitOfWork, token_blacklist: TokenBlacklistService):
        self.uow = uow
        self.token_blacklist = token_blacklist

    async def _authenticate_user(self, email: str, password: str) -> UserORM | None:
        """
        Аутентификация пользователя

        Принимает:
            - почта: str
            - пароль: str

        Возвращает:
            - Объект пользователя базы данных: User
            - Возвращает None в случае, если такого пользователя не существует или пароль неверный
        """

        user = await self.uow.user.get_by_email(email=email)
        if not user:
            return None

        password_is_true = await SecurityService.verify_password(
            plain_password=password, hashed_password=user.password_hash
        )
        if not password_is_true:
            return None

        return user

    async def login_user(self, email: str, password: str) -> tuple[str]:
        """
        Процесс входа пользователя в аккаунт

        Принимает:
            - payload для айтентификации: UserLoginRequest

        Возвращает:
            - access и refresh токены: tuple[str]

        Исключения:
            - аутентификация не пройдена (_authenticate_user вернет None): InvalidPasswordOrEmailException
        """

        user = await self._authenticate_user(email=email, password=password)
        if not user:
            raise InvalidPasswordOrEmailException

        token_payload = self.uow.user.to_token_payload(user=user)
        return SecurityService.create_pair_tokens(data=token_payload)

    async def logout_user(self, refresh_token: str) -> None:
        """
        Процесс выхода пользователя из аккаунта

        Принимает:
            - refresh_token: str

        Исключения:
            - если refresh_token не валидный: InvalidTokenException
        """

        payload = await verify_token(
            token=refresh_token,
            secret_key=config.SECRET_KEY,
            algorithm=config.ALGORITHM,
            expected_type="refresh",
        )
        meta = BlacklistedTokenMeta(
            revoked_at=datetime.datetime.now(datetime.UTC),
            reason="logout",
        )

        await self.token_blacklist.add_to_blacklist(
            jti=payload.get("jti"),
            meta=meta,
            expires_in=config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        )

    async def refresh_access_token(self, user: UserORM) -> str:
        """
        Обновление access_token

        Принимает:
            - пользователя: UserORM

        Возвращает:
            - access токен: str
        """

        token_payload = self.uow.user.to_token_payload(user=user)
        return SecurityService.create_access_token(data=token_payload)
