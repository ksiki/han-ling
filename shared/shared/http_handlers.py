from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from shared.exceptions import AppBaseException


def init_exception_handlers(app: FastAPI) -> None:
    """
    Подключает глобальную обработку общих ошибок к микросервису

    Принимает:
        - инстанс микросервиса: FastAPI
    """

    @app.exception_handler(AppBaseException)
    async def shared_exception_handler(
        request: Request, exc: AppBaseException
    ) -> JSONResponse:
        status_code, headers, message = (
            getattr(exc, "status_code", 500),
            getattr(exc, "headers", {}),
            getattr(exc, "message", ""),
        )

        return JSONResponse(
            status_code=status_code,
            content={"detail": message},
            headers=headers,
        )
