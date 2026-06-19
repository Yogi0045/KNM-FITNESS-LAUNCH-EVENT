"""
Lucky draw service.

Picks a random, eligible (checked-in, not already a winner) participant
and marks them as a winner. Selection happens at the database level
(ORDER BY random() LIMIT 1) so it scales fine even with large guest
lists and stays fair regardless of insertion order.
"""

from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Participant


def pick_winner(db: Session) -> Optional[Participant]:
    """Randomly select an eligible participant and mark them as a winner.

    Returns the winning Participant, or None if there are no eligible
    participants left (i.e. everyone checked-in has already won).
    """
    winner = (
        db.query(Participant)
        .filter(Participant.checked_in == True, Participant.is_winner == False)  # noqa: E712
        .order_by(func.random())
        .first()
    )

    if winner is None:
        return None

    winner.is_winner = True
    db.commit()
    db.refresh(winner)
    return winner
