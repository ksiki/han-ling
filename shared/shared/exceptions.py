class AppBaseException(Exception):
    """Базовый класс для всех ошибок системы"""

    message: str = "Internal server error"
    status_code: int = 500


class InvalidTokenException(AppBaseException):
    message: str = "Token is invalid"
    status_code: int = 401
