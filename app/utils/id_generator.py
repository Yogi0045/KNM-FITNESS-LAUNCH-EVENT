"""
Registration ID generation.

Registration IDs follow the format KNM-00001, KNM-00002, ... and are
generated from a dedicated PostgreSQL sequence (`reg_id_seq`), so number
allocation is atomic even when multiple people register at the exact
same time.
"""

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models import Participant


def calculate_next_reg_id_value(existing_count: int, max_reg_id: int | None, start_at: int = 1) -> int:
    """Return the next numeric value for a registration ID."""
    if existing_count <= 0:
        return start_at
    if max_reg_id is None:
        return existing_count + start_at
    return max(max_reg_id + 1, existing_count + start_at)


def generate_reg_id(db: Session) -> str:
    """Atomically reserve the next registration ID and format it as KNM-00001."""
    existing_count = db.query(Participant).count()

    if existing_count == 0:
        db.execute(text("SELECT setval('reg_id_seq', 1, false)"))
        return "KNM-00001"

    result = db.execute(text("SELECT nextval('reg_id_seq')"))
    next_value = result.scalar()
    if next_value is None:
        next_value = calculate_next_reg_id_value(existing_count, None, start_at=1)
    return f"KNM-{next_value:05d}"
