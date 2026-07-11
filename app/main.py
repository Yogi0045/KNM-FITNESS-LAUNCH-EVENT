"""
FastAPI application entrypoint.

Run with:
    uvicorn app.main:app --reload

On startup this:
  1. Creates all database tables if they don't already exist.
  2. Creates the `reg_id_seq` PostgreSQL sequence if it doesn't exist.
  3. Seeds a default admin account (from ADMIN_USERNAME / ADMIN_PASSWORD
     in the environment) if no admin accounts exist yet.
"""

import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from starlette.middleware.sessions import SessionMiddleware

from app.auth import hash_password
from app.config import settings
from app.database import Base, SessionLocal, engine
from app.models import Admin, reg_id_seq
from app.routes import admin, api, checkin, lucky_draw, public

app = FastAPI(title=settings.EVENT_NAME)

# Session middleware backs the admin "logged in" cookie. SECRET_KEY should
# be a long random string in production (see .env.example).
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# Make sure the directory used to store generated QR codes exists before
# we try to mount it as a static directory.
os.makedirs(settings.QR_CODE_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Routers
app.include_router(public.router)
app.include_router(admin.router)
app.include_router(checkin.router)
app.include_router(lucky_draw.router)
app.include_router(api.router)


@app.on_event("startup")
def on_startup() -> None:
    # 1. Create tables
    Base.metadata.create_all(bind=engine)

    # 2. Ensure the gender column exists for existing databases
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE participants ADD COLUMN IF NOT EXISTS gender VARCHAR(20) NOT NULL DEFAULT 'male'"))

    # 3. Create the registration-ID sequence
    reg_id_seq.create(engine, checkfirst=True)

    # 3. Seed a default admin account if none exists
    db = SessionLocal()
    try:
        existing_admin = db.query(Admin).filter(Admin.username == settings.ADMIN_USERNAME).first()
        if not existing_admin:
            db.add(
                Admin(
                    username=settings.ADMIN_USERNAME,
                    password_hash=hash_password(settings.ADMIN_PASSWORD),
                )
            )
            db.commit()
    finally:
        db.close()


@app.get("/health")
def health_check():
    """Simple health-check endpoint, useful for deployment platforms."""
    return {"status": "ok"}
