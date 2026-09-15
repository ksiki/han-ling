from shared.exceptions import AppBaseException


class CaptchaInvalidException(AppBaseException):
    """
    Любые проблемы с капчей
    """

    message = "Captcha invalid"
    status_code: int = 400


class UserNotFoundException(AppBaseException):
    """
    Исключение если пользователь с таким email не найден
    """

    message = "The user was not found"
    status_code: int = 400


class UserAlreadyExistsException(AppBaseException):
    """
    Исключение если пользователь с таким email уже существует
    """

    message = "The user with this email already exists"
    status_code: int = 409


class UserAlreadyLoggedInException(AppBaseException):
    """
    Исключение если пользователь уже авторизаван
    """

    message = "The user already logged in"
    status_code: int = 400


class UserBannedOrDeletedException(AppBaseException):
    """
    Исключение если пользователь с таким email забанен или удален
    """

    message = "The user is banned or deleted"
    status_code: int = 401


class InvalidPasswordOrEmailException(AppBaseException):
    """
    Исключение если email или пароль введенный пользователь неверный
    """

    message = "Invalid password or user's email address"
    status_code: int = 401


class PasswordsDoNotMatchException(AppBaseException):
    """
    Исключение если пароль и повтор пароля при регистрации не совпадают
    """

    message = "Password and password confirmation do not match"
    status_code: int = 400


class RedisPoolNotInitializedException(AppBaseException):
    """
    Вызывается, если пул Redis не инициализирован
    """

    message = "Redis pool is not initialized"
    status_code: int = 500


class FailedCreateOTPException(AppBaseException):
    """
    Выбрасывается при неуспешном создании OTP по любой причине
    """

    message = "Failed to create an OTP"
    status_code: int = 500


class OTPInvalidException(AppBaseException):
    """
    Выбрасывается при неверном или устаревшем OTP
    """

    message = "OTP invalid"
    status_code: int = 400


class OTPAttemptsExceededException(AppBaseException):
    """
    Выбрасывается при достижении попыток ввода OTP
    """

    message = "OTP attempts exceeded"
    status_code: int = 400
