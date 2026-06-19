"""
SQLAlchemy ORM models.

Participant  -- one row per registered attendee
Admin        -- staff/admin accounts used to log into the dashboard
reg_id_seq   -- a PostgreSQL sequence used to atomically generate the
                human readable registration IDs (KNM-00001, KNM-00002, ...)
"""

import uuid

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, Sequence, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database import Base

# Dedicated DB sequence used to generate sequential registration numbers.
# Creating it as an explicit Sequence (rather than an autoincrement column)
# lets us reserve a number atomically *before* we know the rest of the row,
# which keeps reg_id generation safe under concurrent registrations.
reg_id_seq = Sequence("reg_id_seq", start=1)


class Participant(Base):
    __tablename__ = "participants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reg_id = Column(String(20), unique=True, nullable=False, index=True)

    name = Column(String(120), nullable=False)
    age = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    city = Column(String(100), nullable=False)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(150), unique=True, nullable=False, index=True)

    qr_path = Column(String(255), nullable=True)

    checked_in = Column(Boolean, default=False, nullable=False)
    check_in_time = Column(DateTime(timezone=True), nullable=True)

    is_winner = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:  # pragma: no cover - debugging helper only
        return f"<Participant {self.reg_id} - {self.name}>"


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:  # pragma: no cover - debugging helper only
        return f"<Admin {self.username}>"
