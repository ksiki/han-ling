from fastapi import APIRouter, BackgroundTasks, Depends, Request, Response, status

from src.api.dependencies import (
    get_registration_cases,
)
from src.background_tasks.email import send_otp_email
from src.core.settings import config
from src.schemas.common import SuccessResponse
from src.schemas.register import (
    RegisterSendOTPRequest,
    ResendOTPRequest,
    VerifyOTPRequest,
)
from src.use_cases import RegistrationCases

router = APIRouter(prefix="/register", tags="Registration v1")


@router.post(
    "/send-otp", status_code=status.HTTP_200_OK, response_model=SuccessResponse
)
async def send_otp(
    payload: RegisterSendOTPRequest,
    background_tasks: BackgroundTasks,
    registration_cases: RegistrationCases = Depends(get_registration_cases),
) -> SuccessResponse:
    """Инициирует процесс регистрации пользователя с отправкой одноразового кода.

    Args:
        payload: Данные запроса на регистрацию (email, пароль, токен капчи).
        background_tasks: Менеджер фоновых задач FastAPI для отправки письма с кодом.
        registration_cases: Сценарий (Use Case) управления процессом регистрации.

    Returns:
        SuccessResponse: Подтверждение успешной отправки запроса.
    """
    otp = await registration_cases.begin_registration(
        captcha_token=payload.captcha_token,
        email=payload.email,
        password=payload.password,
    )
    background_tasks.add_task(send_otp_email, email_to=payload.email, otp_code=otp)

    return SuccessResponse()


@router.post(
    "/resend-otp", status_code=status.HTTP_200_OK, response_model=SuccessResponse
)
async def resend_otp(
    payload: ResendOTPRequest,
    background_tasks: BackgroundTasks,
    registration_cases: RegistrationCases = Depends(get_registration_cases),
) -> SuccessResponse:
    """Генерирует и отправляет новый OTP-код на указанный email.

    Args:
        payload: Данные запроса с адресом электронной почты пользователя.
        background_tasks: Менеджер фоновых задач FastAPI для отправки письма с новым кодом.
        registration_cases: Сценарий (Use Case) управления процессом регистрации.

    Returns:
        SuccessResponse: Подтверждение успешной повторной отправки кода.
    """
    new_otp = await registration_cases.resend_otp(email=payload.email)
    background_tasks.add_task(send_otp_email, email_to=payload.email, otp_code=new_otp)

    return SuccessResponse()


@router.post(
    "/verify", status_code=status.HTTP_201_CREATED, response_model=SuccessResponse
)
async def verify(
    payload: VerifyOTPRequest,
    request: Request,
    response: Response,
    registration_cases: RegistrationCases = Depends(get_registration_cases),
) -> SuccessResponse:
    """Подтверждает регистрацию по OTP-коду, создает аккаунт и выставляет токены в куки.

    Args:
        payload: Данные подтверждения, содержащие email и введенный OTP-код.
        request: Объект входящего HTTP-запроса для извлечения сетевых метаданных (IP, User-Agent).
        response: Объект HTTP-ответа для записи авторизационных кук (access и refresh токенов).
        registration_cases: Сценарий (Use Case) управления процессом регистрации.

    Returns:
        SuccessResponse: Подтверждение успешного завершения регистрации и создания пользователя.
    """
    ip = request.headers.get(
        "X-Forwarded-For", request.client.host if request.client else "Unknown"
    )
    user_agent = request.headers.get("User-Agent", "Unknown")

    access_token, refresh_token = await registration_cases.verify(
        email=payload.email, otp=payload.otp, ip=ip, user_agent=user_agent
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
