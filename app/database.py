"""
Database engine and session management.

Exposes:
    - engine        : SQLAlchemy engine bound to the PostgreSQL DATABASE_URL
    - SessionLocal   : session factory
    - Base           : declarative base class for all ORM models
    - get_db()       : FastAPI dependency that yields a request-scoped session
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that provides a database session per-request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
