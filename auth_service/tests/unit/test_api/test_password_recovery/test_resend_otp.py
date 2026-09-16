async def test_resend_otp_success(
    unit_client, mock_password_recovery_cases, mock_send_email_password_recovery
) -> None:
    payload = {
        "email": "test@example.com",
    }

    response = await unit_client.post("/password-reset/resend-otp", json=payload)

    assert response.status_code == 200

    mock_password_recovery_cases.resend_otp.assert_awaited_once_with(
        email=payload["email"]
    )

    mock_send_email_password_recovery.assert_called_once_with(
        email_to=payload["email"],
        otp_code="654321",
    )


async def test_resend_otp_invalid_email(
    unit_client, mock_password_recovery_cases, mock_send_email_password_recovery
) -> None:
    payload = {
        "email": "invalid-email-format",
    }

    response = await unit_client.post("/password-reset/send-otp", json=payload)

    assert response.status_code == 422

    mock_password_recovery_cases.resend_otp.assert_not_awaited()
    mock_send_email_password_recovery.assert_not_called()
