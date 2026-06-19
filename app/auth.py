"""
Authentication helpers: password hashing/verification and a dependency
for protecting JSON/API endpoints that require an authenticated admin.

Page routes (dashboard, check-in, lucky draw) check
`request.session.get("admin_username")` directly and redirect to the
login page when absent -- see the individual route modules. This module
provides the password utilities plus a reusable dependency for the JSON
API endpoints, which should return 401 instead of redirecting.
"""

from fastapi import Depends, HTTPException, Request, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Admin

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def admin_required_api(request: Request, db: Session = Depends(get_db)) -> Admin:
    """Dependency for JSON API endpoints. Raises 401 if not logged in."""
    username = request.session.get("admin_username")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    admin = db.query(Admin).filter(Admin.username == username).first()
    if not admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    return admin
