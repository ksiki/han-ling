import logging

from src.core.http import http_client
from src.core.settings import config

logger = logging.getLogger(__name__)


async def send_otp_email(email_to: str, otp_code: str) -> None:
    """Отправляет одноразовый код подтверждения (OTP) на электронную почту.

    Args:
        email_to: Адрес электронной почты получателя.
        otp_code: Одноразовый код подтверждения для отправки.
    """

    payload = {
        "from": f"noreply@{config.DOMAIN}",
        "to": [email_to],
        "subject": f"Ваш код подтверждения | {config.PRODUCT_NAME}",
        "html": f"Ваш проверочный код: {otp_code}\nКод действителен ограниченное время.",
    }
    headers = {
        "Authorization": f"Bearer {config.RESEND_API_KEY}",
        "Content-Type": "application/json",
    }

    response = await http_client.post(config.RESEND_URL, json=payload, headers=headers)

    if response.status_code not in (200, 201):
        logger.info(f"Resend API Error: {response.text}. Sent OTP to {email_to} failed")
    else:
        logger.info(f"OTP send to {email_to} is successful")
