"""
QR check-in routes.

/checkin                       -- staff-facing page with the camera scanner
/api/participant/{reg_id}      -- look up a participant by registration ID
/api/checkin/{reg_id}          -- mark a participant as checked in
"""

from datetime import datetime

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Participant

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/checkin", response_class=HTMLResponse)
def checkin_page(request: Request):
    if not request.session.get("admin_username"):
        return RedirectResponse(url="/admin/login", status_code=303)
    return templates.TemplateResponse(
        request, "checkin.html", {"event_name": settings.EVENT_NAME}
    )


def _serialize_participant(p: Participant) -> dict:
    return {
        "reg_id": p.reg_id,
        "name": p.name,
        "age": p.age,
        "weight": p.weight,
        "city": p.city,
        "phone": p.phone,
        "email": p.email,
        "checked_in": p.checked_in,
        "check_in_time": p.check_in_time.strftime("%Y-%m-%d %H:%M:%S") if p.check_in_time else None,
    }


@router.get("/api/participant/{reg_id}")
def lookup_participant(reg_id: str, request: Request, db: Session = Depends(get_db)):
    if not request.session.get("admin_username"):
        return JSONResponse({"success": False, "message": "Not authenticated"}, status_code=401)

    clean_reg_id = reg_id.strip().upper()
    participant = db.query(Participant).filter(Participant.reg_id == clean_reg_id).first()

    if not participant:
        return JSONResponse(
            {"success": False, "message": f"No participant found for {clean_reg_id}"}, status_code=404
        )

    return JSONResponse({"success": True, "participant": _serialize_participant(participant)})


@router.post("/api/checkin/{reg_id}")
def checkin_participant(reg_id: str, request: Request, db: Session = Depends(get_db)):
    if not request.session.get("admin_username"):
        return JSONResponse({"success": False, "message": "Not authenticated"}, status_code=401)

    clean_reg_id = reg_id.strip().upper()
    participant = db.query(Participant).filter(Participant.reg_id == clean_reg_id).first()

    if not participant:
        return JSONResponse(
            {"success": False, "message": f"No participant found for {clean_reg_id}"}, status_code=404
        )

    if participant.checked_in:
        return JSONResponse(
            {
                "success": False,
                "message": "Already Checked In",
                "participant": _serialize_participant(participant),
            }
        )

    participant.checked_in = True
    participant.check_in_time = datetime.utcnow()
    db.commit()
    db.refresh(participant)

    return JSONResponse(
        {
            "success": True,
            "message": "Checked in successfully",
            "participant": _serialize_participant(participant),
        }
    )
