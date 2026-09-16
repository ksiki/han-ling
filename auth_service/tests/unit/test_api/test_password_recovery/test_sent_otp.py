async def test_send_otp_success(
    unit_client, mock_password_recovery_cases, mock_send_email_password_recovery
) -> None:
    payload = {
        "email": "test@example.com",
        "captcha_token": "valid_turnstile_token",
    }

    response = await unit_client.post("/password-reset/send-otp", json=payload)

    assert response.status_code == 200

    mock_password_recovery_cases.begin_password_recovery.assert_awaited_once_with(
        captcha_token=payload["captcha_token"],
        email=payload["email"],
    )

    mock_send_email_password_recovery.assert_called_once_with(
        email_to=payload["email"],
        otp_code="123456",
    )


async def test_send_otp_invalid_email(
    unit_client, mock_password_recovery_cases, mock_send_email_password_recovery
) -> None:
    payload = {
        "email": "invalid-email-format",
        "captcha_token": "valid_token",
    }

    response = await unit_client.post("/register/send-otp", json=payload)

    assert response.status_code == 422

    mock_password_recovery_cases.begin_password_recovery.assert_not_awaited()
    mock_send_email_password_recovery.assert_not_called()
