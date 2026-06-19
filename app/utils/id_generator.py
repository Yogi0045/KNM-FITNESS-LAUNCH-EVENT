"""
Registration ID generation.

Registration IDs follow the format KNM-00001, KNM-00002, ... and are
generated from a dedicated PostgreSQL sequence (`reg_id_seq`), so number
allocation is atomic even when multiple people register at the exact
same time.
"""

from sqlalchemy import text
from sqlalchemy.orm import Session


def generate_reg_id(db: Session) -> str:
    """Atomically reserve the next sequence value and format it as KNM-00001."""
    result = db.execute(text("SELECT nextval('reg_id_seq')"))
    next_value = result.scalar()
    return f"KNM-{next_value:05d}"
