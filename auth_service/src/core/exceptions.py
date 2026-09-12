from fastapi import status
from shared.exceptions import AppBaseException


class UserAlreadyExistsException(AppBaseException):
    """
    Исключение если пользователь с таким email уже существует
    """

    message = "The user with this email already exists"
    status_code: int = status.HTTP_409_CONFLICT


class InvalidPasswordOrEmailException(AppBaseException):
    """
    Исключение если email или пароль введенный пользователь неверный
    """

    message = "Invalid password or user's email address"
    status_code: int = status.HTTP_401_UNAUTHORIZED


class PasswordsDoNotMatchException(AppBaseException):
    """
    Исключение если пароль и повтор пароля при регистрации не совпадают
    """

    message = "Password and password confirmation do not match"
    status_code: int = status.HTTP_400_BAD_REQUEST


class RedisPoolNotInitializedException(AppBaseException):
    """
    Вызывается, если пул Redis не инициализирован
    """

    message = "Redis pool is not initialized"
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
