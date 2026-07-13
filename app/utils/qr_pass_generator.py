"""
Generates a professional QR Pass (PNG) for a participant, combining
event branding with their already-generated QR code image.

This does NOT regenerate the QR code or touch the database -- it only
composes an image using the QR code file that qr_service already created.
"""

import os
from PIL import Image, ImageDraw, ImageFont

from app.config import settings

PASS_DIR = "app/static/passes"
LOGO_PATH = "app/static/img/logo.png"  # optional -- used only if it exists

WIDTH, HEIGHT = 900, 1300
BG_COLOR = (10, 10, 26)          # dark navy
GOLD = (212, 175, 55)
WHITE = (245, 245, 245)
GRAY = (160, 160, 170)


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _centered_text(draw, text, y, font, fill, canvas_width=WIDTH):
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    draw.text(((canvas_width - w) / 2, y), text, font=font, fill=fill)


def generate_qr_pass(reg_id: str, name: str, qr_file_path: str) -> str:
    """
    Builds the QR Pass PNG and saves it to disk.

    Returns the file system path to the generated pass image.
    """
    os.makedirs(PASS_DIR, exist_ok=True)
    out_path = os.path.join(PASS_DIR, f"{reg_id}_QR_Pass.png")

    canvas = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(canvas)

    # Gold border
    draw.rectangle([15, 15, WIDTH - 15, HEIGHT - 15], outline=GOLD, width=3)

    y = 60

    # Logo (optional)
    if os.path.exists(LOGO_PATH):
        logo = Image.open(LOGO_PATH).convert("RGBA")
        logo.thumbnail((160, 160))
        canvas.paste(logo, ((WIDTH - logo.width) // 2, y), logo)
        y += logo.height + 20
    else:
        _centered_text(draw, "KNM FITNESS", y, _font(40, bold=True), GOLD)
        y += 60

    # Event name
    _centered_text(draw, settings.EVENT_NAME, y, _font(30, bold=True), WHITE)
    y += 50

    # Event date / location
    if getattr(settings, "EVENT_DATE", None):
        _centered_text(draw, str(settings.EVENT_DATE), y, _font(22), GRAY)
        y += 34
    if getattr(settings, "EVENT_LOCATION", None):
        _centered_text(draw, str(settings.EVENT_LOCATION), y, _font(22), GRAY)
        y += 50

    # Divider
    draw.line([(60, y), (WIDTH - 60, y)], fill=GOLD, width=1)
    y += 40

    # Participant details
    _centered_text(draw, name, y, _font(34, bold=True), WHITE)
    y += 50
    _centered_text(draw, reg_id, y, _font(26, bold=True), GOLD)
    y += 60

    # QR code
    qr_img = Image.open(qr_file_path).convert("RGB")
    qr_size = 480
    qr_img = qr_img.resize((qr_size, qr_size))

    # White padding behind QR for scan reliability
    pad = 24
    qr_bg = Image.new("RGB", (qr_size + pad * 2, qr_size + pad * 2), WHITE)
    qr_bg.paste(qr_img, (pad, pad))
    canvas.paste(qr_bg, ((WIDTH - qr_bg.width) // 2, y))
    y += qr_bg.height + 30

    # Footer
    _centered_text(draw, "Present this QR code at check-in", y, _font(20), GRAY)

    canvas.save(out_path, "PNG")
    return out_path