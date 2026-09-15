from fastapi import APIRouter, BackgroundTasks, Depends, Request, Response, status

from src.api.dependencies import get_password_recovery_cases
from src.background_tasks.email import send_otp_email
from src.core.settings import config
from src.schemas.common import ResendOTPRequest, SuccessResponse
from src.schemas.recovery import PasswordResetConfirmRequest, PasswordResetSendRequest
from src.use_cases import PasswordResetCaces

router = APIRouter(prefix="/password-reset", tags=["Password Recovery v1"])


@router.post(
    "/send-otp", status_code=status.HTTP_200_OK, response_model=SuccessResponse
)
async def send_otp(
    payload: PasswordResetSendRequest,
    background_tasks: BackgroundTasks,
    password_reset_cases: PasswordResetCaces = Depends(get_password_recovery_cases),
) -> SuccessResponse:
    """Инициирует процесс сброса пароля с отправкой проверочного OTP-кода.

    Args:
        payload: Данные запроса на сброс пароля (email, токен капчи).
        background_tasks: Менеджер фоновых задач FastAPI для отправки письма с кодом.
        password_reset_cases: Сценарий (Use Case) управления процессом сброса пароля.

    Returns:
        SuccessResponse: Подтверждение успешной отправки запроса.
    """
    otp = await password_reset_cases.begin_password_recovery(
        captcha_token=payload.captcha_token,
        email=payload.email,
    )
    background_tasks.add_task(send_otp_email, email_to=payload.email, otp_code=otp)

    return SuccessResponse()


@router.post(
    "/resend-otp", status_code=status.HTTP_200_OK, response_model=SuccessResponse
)
async def resend_otp(
    payload: ResendOTPRequest,
    background_tasks: BackgroundTasks,
    password_reset_cases: PasswordResetCaces = Depends(get_password_recovery_cases),
) -> SuccessResponse:
    """Повторно формирует и отправляет проверочный OTP-код для восстановления пароля.

    Args:
        payload: Данные запроса с адресом электронной почты пользователя.
        background_tasks: Менеджер фоновых задач FastAPI для отправки письма.
        password_reset_cases: Сценарий (Use Case) управления процессом сброса пароля.

    Returns:
        SuccessResponse: Подтверждение успешной генерации нового кода.
    """
    new_otp = await password_reset_cases.resend_otp(email=payload.email)
    background_tasks.add_task(send_otp_email, email_to=payload.email, otp_code=new_otp)

    return SuccessResponse()


@router.post("/confirm", status_code=status.HTTP_200_OK, response_model=SuccessResponse)
async def confirm(
    payload: PasswordResetConfirmRequest,
    request: Request,
    response: Response,
    password_reset_cases: PasswordResetCaces = Depends(get_password_recovery_cases),
) -> SuccessResponse:
    """Подтверждает сброс пароля по коду, обновляет учетные данные и устанавливает сессионные куки.

    Args:
        payload: Данные подтверждения (email, OTP-код, новый пароль).
        request: Объект текущего HTTP-запроса для извлечения сетевых метаданных (IP, User-Agent).
        response: Объект HTTP-ответа для записи авторизационных токенов в cookie.
        password_reset_cases: Сценарий (Use Case) управления процессом сброса пароля.

    Returns:
        SuccessResponse: Подтверждение успешного обновления пароля и входа в систему.
    """
    ip = request.headers.get(
        "X-Forwarded-For", request.client.host if request.client else "Unknown"
    )
    user_agent = request.headers.get("User-Agent", "Unknown")

    access_token, refresh_token = await password_reset_cases.finish_password_recovery(
        email=payload.email,
        otp=payload.otp,
        new_password=payload.new_password,
        ip=ip,
        user_agent=user_agent,
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=not config.DEBUG,
        samesite="lax",
        max_age=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=not config.DEBUG,
        samesite="lax",
        max_age=config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return SuccessResponse()
