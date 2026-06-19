"""
Lightweight JSON API used by the dashboard for live stat polling
(AJAX). Kept separate from the page routes in admin.py for clarity.
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Participant

router = APIRouter(prefix="/api")


@router.get("/stats")
def get_stats(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("admin_username"):
        return JSONResponse({"success": False, "message": "Not authenticated"}, status_code=401)

    total = db.query(Participant).count()
    checked_in = db.query(Participant).filter(Participant.checked_in == True).count()  # noqa: E712
    pending = total - checked_in

    return JSONResponse({"success": True, "total": total, "checked_in": checked_in, "pending": pending})
