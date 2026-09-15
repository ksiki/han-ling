import logging
from email.message import EmailMessage

from aiosmtplib import send

from src.core.settings import config

logger = logging.getLogger(__name__)


async def send_otp_email(email_to: str, otp_code: str) -> None:
    """Отправляет одноразовый код подтверждения (OTP) на электронную почту.

    Args:
        email_to: Адрес электронной почты получателя.
        otp_code: Одноразовый код подтверждения для отправки.
    """
    message = EmailMessage()
    message["From"] = config.SENDER_EMAIL
    message["To"] = email_to
    message["Subject"] = "Ваш код подтверждения | HanLing"
    message.set_content(
        f"Ваш проверочный код: {otp_code}\nКод действителен ограниченное время."
    )

    try:
        await send(
            message,
            hostname=config.SMTP_HOST,
            port=config.SMTP_PORT,
        )
        logger.info(f"OTP успешно отправлен на {email_to}")
    except Exception as e:
        logger.error(f"Ошибка при отправке OTP на {email_to}: {e}")
