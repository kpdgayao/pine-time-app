import os
import smtplib
from email.message import EmailMessage
import logging

def send_reset_email(to_email: str, reset_token: str) -> bool:
    """
    Sends a password reset email with the given token.
    Returns True if sent successfully, False otherwise.
    """
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    sender_email = os.getenv('SMTP_SENDER', smtp_user)

    if not (smtp_host and smtp_user and smtp_password and sender_email):
        logging.error("SMTP configuration is incomplete. Email not sent.")
        return False

    msg = EmailMessage()
    msg['Subject'] = 'Pine Time Password Reset'
    msg['From'] = sender_email
    msg['To'] = to_email
    msg.set_content(f"""
Hello,

You requested a password reset for your Pine Time account.

Your password reset token is:

{reset_token}

This token is valid for 1 hour. If you did not request this, please ignore this email.

Best regards,
Pine Time Team
""")
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        logging.info(f"Password reset email sent to {to_email}")
        return True
    except Exception as e:
        logging.error(f"Failed to send password reset email: {e}")
        return False
