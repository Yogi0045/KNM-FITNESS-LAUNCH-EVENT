from dotenv import load_dotenv
import os
import logging
import smtplib
import urllib.request
import urllib.parse
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

    host = os.getenv("MAIL_SERVER", "smtp.resend.com").strip()
    username = os.getenv("MAIL_USERNAME", "").strip()

    if host.lower().endswith("resend.com"):
        if not username or "@" in username:
            username = "resend"

    return {
        "username": username,
        "password": password,
        "from": os.getenv("MAIL_FROM", "onboarding@yourdomain.com").strip(),
        "host": host,
        "port": int(os.getenv("MAIL_PORT", "587")),
    }


def _get_sms_config():
    return {
        "enabled": os.getenv("SMS_ENABLED", "false").strip().lower() == "true",
        "gateway_url": os.getenv("SMS_GATEWAY_URL", "").strip(),
        "phone_number": os.getenv("SMS_PHONE_NUMBER", "").strip(),
        "api_key": os.getenv("SMS_API_KEY", "").strip(),
    }


def _send_sms_notification(message: str, phone_number: str | None = None) -> None:
    cfg = _get_sms_config()
    if not cfg["enabled"]:
        return

    target_phone = phone_number or cfg["phone_number"]
    if not target_phone or not cfg["gateway_url"]:
        return

    payload = urllib.parse.urlencode({"to": target_phone, "message": message, "api_key": cfg["api_key"]}).encode("utf-8")
    req = urllib.request.Request(cfg["gateway_url"], data=payload, method="POST")
    with urllib.request.urlopen(req, timeout=15) as response:
        response.read()


async def send_registration_email(email, name, qr_path, phone_number: str | None = None):
    """Send registration email with QR image attached using SMTP.

    If SMTP credentials are not configured this logs a warning and returns
    so registration can complete without blocking.
    """
    cfg = _get_smtp_config()

    if not cfg["username"] or not cfg["password"]:
        logger.warning(
            f"Email credentials not configured. Skipping email to {email}."
        )
        if phone_number:
            _send_sms_notification(
                f"KNM registration successful for {name}. QR details will be sent by email when configured.",
                phone_number,
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
    finally:
        if phone_number:
            sms_message = f"KNM registration successful for {name}. QR sent to email: {email}."
            _send_sms_notification(sms_message, phone_number)