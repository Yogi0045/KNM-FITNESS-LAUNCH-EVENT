from dotenv import load_dotenv
import os
import logging
import smtplib
import urllib.request
import urllib.parse
from email.message import EmailMessage
import resend


class EmailDeliveryError(Exception):
    pass

load_dotenv()

logger = logging.getLogger(__name__)


def _get_smtp_config():
    password = os.getenv("MAIL_PASSWORD", "").strip()
    if password and " " in password:
        password = password.replace(" ", "")

    host = os.getenv("MAIL_SERVER", "smtp.gmail.com").strip()
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


def send_registration_email(email, name, qr_path, phone_number: str | None = None):
    """Send registration email with QR image attached using SMTP.

    If SMTP credentials are not configured this logs a warning and returns
    so registration can complete without blocking.
    """
    cfg = _get_smtp_config()
    resend_api_key = os.getenv("RESEND_API_KEY", "").strip()
    sender = cfg["from"] or cfg["username"]

    if not resend_api_key and (not cfg["username"] or not cfg["password"]):
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
        body = f"""
Hello {name},

Your registration has been confirmed.

Please find your QR code attached. Show this QR code during check-in.

Thank you,
KNM Fitness
"""

        attachment_data = None
        if qr_path and os.path.exists(qr_path):
            with open(qr_path, "rb") as f:
                qr_bytes = f.read()
            attachment_data = {
                "content": list(qr_bytes),
                "filename": os.path.basename(qr_path),
            }

        if resend_api_key:
            logger.debug("Sending registration email through Resend API")
            os.environ["RESEND_API_KEY"] = resend_api_key
            params = resend.Emails.SendParams(
                from_=sender,
                to=email,
                subject="KNM Fitness Registration Successful",
                text=body,
            )
            if attachment_data:
                params["attachments"] = [attachment_data]
            response = resend.Emails.send(params)
            response_id = getattr(response, "id", None) or response.get("id", "unknown") if hasattr(response, "get") else "unknown"
            logger.info("Registration email sent to %s via Resend: %s", email, response_id)
        else:
            logger.debug("Resend API key not configured; using SMTP fallback")
            msg = EmailMessage()
            msg["Subject"] = "KNM Fitness Registration Successful"
            msg["From"] = sender
            msg["To"] = email
            msg.set_content(body)

            if attachment_data:
                msg.add_attachment(bytes(attachment_data["content"]), maintype="image", subtype="png", filename=attachment_data["filename"])

            if cfg["port"] == 465:
                logger.debug("Using SMTP_SSL on port 465")
                with smtplib.SMTP_SSL(cfg["host"], cfg["port"], timeout=20) as server:
                    server.login(cfg["username"], cfg["password"])
                    server.send_message(msg)
                    logger.info(f"Registration email sent to {email} via SSL")
            else:
                logger.debug("Using STARTTLS on port %s", cfg["port"])
                with smtplib.SMTP(cfg["host"], cfg["port"], timeout=20) as server:
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                    server.login(cfg["username"], cfg["password"])
                    server.send_message(msg)
                    logger.info(f"Registration email sent to {email} via STARTTLS")
    except Exception as e:
        logger.error(f"Failed to send registration email to {email}: {e}")
        raise EmailDeliveryError(str(e)) from e
    finally:
        if phone_number:
            sms_message = f"KNM registration successful for {name}. QR sent to email: {email}."
            _send_sms_notification(sms_message, phone_number)