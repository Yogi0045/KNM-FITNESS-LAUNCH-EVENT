"""
QR code generation service.

Generates a QR code image encoding {"reg_id": "KNM-00001"} and saves it
to the configured QR_CODE_DIR, returning the web-accessible path (served
via the /static mount) that gets stored on the participant's qr_path
column.
"""

import json
import os

import qrcode

from app.config import settings


def generate_qr_code(reg_id: str) -> tuple[str, str]:
    """Generate a QR code for the given registration ID and save it to disk.

    Returns a tuple of (web_path, filesystem_path):
    - web_path: the URL path (e.g. /static/qrcodes/KNM-00001.png) that can be
      used directly in an <img> tag and stored in the database.
    - filesystem_path: the actual filesystem path for file operations like email attachments.
    """
    os.makedirs(settings.QR_CODE_DIR, exist_ok=True)

    qr_payload = json.dumps({"reg_id": reg_id})

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_payload)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    filename = f"{reg_id}.png"
    filepath = os.path.join(settings.QR_CODE_DIR, filename)
    img.save(filepath)

    web_path = f"/static/qrcodes/{filename}"
    return web_path, filepath
