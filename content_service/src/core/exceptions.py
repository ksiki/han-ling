from shared.exceptions import AppBaseException


class RedisPoolNotInitializedException(AppBaseException):
    """
    Вызывается, если пул Redis не инициализирован
    """

    message = "Redis pool is not initialized"
    status_code: int = 500
