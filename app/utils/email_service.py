from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import load_dotenv
import os
import logging

load_dotenv()

logger = logging.getLogger(__name__)

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME", ""),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", ""),
    MAIL_FROM=os.getenv("MAIL_FROM", "noreply@knmfitness.com"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)

async def send_registration_email(email, name, qr_path):
    """Send registration email with QR code attachment.
    
    If email credentials are not configured, this function logs a warning
    and completes gracefully without sending. This allows the app to work
    in development/test mode without email setup.
    """
    # Check if email is configured
    if not conf.MAIL_USERNAME or not conf.MAIL_PASSWORD:
        logger.warning(
            f"Email credentials not configured. Skipping email to {email}. "
            "Set MAIL_USERNAME and MAIL_PASSWORD environment variables to enable email."
        )
        return
    
    try:
        message = MessageSchema(
            subject="KNM Fitness Registration Successful",
            recipients=[email],
            body=f"""
Hello {name},

Your registration has been confirmed.

Please find your QR code attached.

Show this QR code during check-in.

Thank you,
KNM Fitness
""",
            subtype="plain",
            attachments=[qr_path]
        )

        fm = FastMail(conf)
        await fm.send_message(message)
        logger.info(f"Registration email sent to {email}")
    except Exception as e:
        logger.error(f"Failed to send registration email to {email}: {e}")
        # Don't raise - allow registration to complete even if email fails