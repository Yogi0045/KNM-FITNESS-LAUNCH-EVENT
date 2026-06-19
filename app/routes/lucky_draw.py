"""
Lucky draw routes: the staff-facing page plus the "pick a winner" action.
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Participant
from app.services.lucky_draw_service import pick_winner

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/lucky-draw", response_class=HTMLResponse)
def lucky_draw_page(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("admin_username"):
        return RedirectResponse(url="/admin/login", status_code=303)

    winners = (
        db.query(Participant)
        .filter(Participant.is_winner == True)  # noqa: E712
        .order_by(Participant.created_at.desc())
        .all()
    )
    eligible_count = (
        db.query(Participant)
        .filter(Participant.checked_in == True, Participant.is_winner == False)  # noqa: E712
        .count()
    )

    return templates.TemplateResponse(
        request,
        "lucky_draw.html",
        {
            "event_name": settings.EVENT_NAME,
            "winners": winners,
            "eligible_count": eligible_count,
        },
    )


@router.post("/lucky-draw/pick")
def pick_winner_route(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("admin_username"):
        return JSONResponse({"success": False, "message": "Not authenticated"}, status_code=401)

    winner = pick_winner(db)
    if not winner:
        return JSONResponse({"success": False, "message": "No eligible participants remaining for the draw."})

    return JSONResponse(
        {
            "success": True,
            "winner": {
                "name": winner.name,
                "reg_id": winner.reg_id,
                "city": winner.city,
            },
        }
    )
