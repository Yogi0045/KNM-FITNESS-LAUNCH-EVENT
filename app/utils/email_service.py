from dotenv import load_dotenv
import os
import logging
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from email.mime.base import MIMEBase
from email import encoders


class EmailDeliveryError(Exception):
    pass

load_dotenv()

logger = logging.getLogger(__name__)


def _get_smtp_config():
    password = os.getenv("MAIL_PASSWORD", "").strip()
    if password and " " in password:
        password = password.replace(" ", "")

    return {
        "username": os.getenv("MAIL_USERNAME", "").strip(),
        "password": password,
        "from": os.getenv("MAIL_FROM", "noreply@knmfitness.com").strip(),
        "host": os.getenv("MAIL_SERVER", "smtp.gmail.com").strip(),
        "port": int(os.getenv("MAIL_PORT", "587")),
    }


async def send_registration_email(email, name, qr_path):
    """Send registration email with QR image attached using SMTP.

    If SMTP credentials are not configured this logs a warning and returns
    so registration can complete without blocking.
    """
    cfg = _get_smtp_config()

    if not cfg["username"] or not cfg["password"]:
        logger.warning(
            f"Email credentials not configured. Skipping email to {email}."
        )
        return

    try:
        msg = EmailMessage()
        msg["Subject"] = "KNM Fitness Registration Successful"
        msg["From"] = formataddr(("KNM Fitness", cfg["from"]))
        msg["To"] = email
        body = f"""
Hello {name},

Your registration has been confirmed.

Please find your QR code attached. Show this QR code during check-in.

Thank you,
KNM Fitness
"""
        msg.set_content(body)

        # Attach QR image
        if qr_path and os.path.exists(qr_path):
            with open(qr_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            filename = os.path.basename(qr_path)
            part.add_header("Content-Disposition", f"attachment; filename=\"{filename}\"")
            msg.add_attachment(part.get_payload(decode=True), maintype="image", subtype="png", filename=filename)

        # Connect and send
        with smtplib.SMTP(cfg["host"], cfg["port"], timeout=20) as server:
            server.starttls()
            server.login(cfg["username"], cfg["password"])
            server.send_message(msg)

        logger.info(f"Registration email sent to {email}")
    except Exception as e:
        logger.error(f"Failed to send registration email to {email}: {e}")
        raise EmailDeliveryError(str(e)) from e