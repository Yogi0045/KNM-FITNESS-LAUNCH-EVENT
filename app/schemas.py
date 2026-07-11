"""
Pydantic schemas used for request validation and API responses.
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class ParticipantCreate(BaseModel):
    """Validates incoming registration form data."""

    name: str = Field(..., min_length=2, max_length=120)
    age: int = Field(..., ge=10, le=100)
    weight: float = Field(..., gt=0, le=400)
    city: str = Field(..., min_length=2, max_length=100)
    gender: str = Field(..., min_length=4, max_length=20)
    phone: str = Field(..., min_length=7, max_length=20)
    email: EmailStr
    instagram_followed: bool = Field(...)

    @field_validator("name", "city", "gender")
    @classmethod
    def strip_text(cls, v: str) -> str:
        return v.strip()

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        normalized = v.strip().lower()
        if normalized not in {"male", "female"}:
            raise ValueError("Gender must be either male or female")
        return normalized

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        cleaned = v.strip().replace(" ", "").replace("-", "")
        digits_only = cleaned.replace("+", "")
        if not digits_only.isdigit():
            raise ValueError("Phone number must contain only digits")
        if len(digits_only) < 10:
            raise ValueError("Phone number is too short")
        return cleaned


class ParticipantResponse(BaseModel):
    id: uuid.UUID
    reg_id: str
    name: str
    age: int
    weight: float
    city: str
    phone: str
    email: str
    qr_path: Optional[str] = None
    checked_in: bool
    check_in_time: Optional[datetime] = None
    is_winner: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminLogin(BaseModel):
    username: str
    password: str


class CheckInResult(BaseModel):
    success: bool
    message: str
