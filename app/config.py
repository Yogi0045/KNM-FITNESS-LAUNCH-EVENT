"""
Application configuration.

All settings are read from environment variables (or a .env file in the
project root). Sensible defaults are provided so the app can be run
out-of-the-box for local development/demo purposes -- change them in
production via a real .env file or real environment variables.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Database -----------------------------------------------------
    DATABASE_URL: str = "postgresql://postgres:yogendraadiyarapu@localhost:5432/knm_fitness"

    # --- Security -------------------------------------------------------
    SECRET_KEY: str = "change-this-secret-key-in-production"

    # --- Default admin account (auto-created on first run) -------------
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"

    # --- Event details (shown on the public site) -----------------------
    EVENT_NAME: str = "KNM Fitness Anakapalle LAUNCH EVENT"
    EVENT_DATE: str = "JULY 12, 2026 (SUNDAY)| 8:00 AM Onwards"
    EVENT_LOCATION: str = "KNM Fitness, Anakapalle, Andhra Pradesh"
    EVENT_DESCRIPTION: str = (
        "Join us for the grand launch of KNM Fitness Anakapalle! Experience "
        "world-class equipment, expert trainers, and an electrifying "
        "community ready to help you crush your fitness goals. Register "
        "now to reserve your spot and stand a chance to win exciting "
        "launch-day prizes."
    )

    # --- File storage -----------------------------------------------------
    QR_CODE_DIR: str = "app/static/qrcodes"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
