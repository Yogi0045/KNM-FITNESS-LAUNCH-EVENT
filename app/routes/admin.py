"""
Admin routes: login/logout, the stats dashboard, and the Excel export
endpoint. All of these (other than the login page itself) require an
active admin session.
"""

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import verify_password
from app.config import settings
from app.database import get_db
from app.models import Admin, Participant
from app.services.excel_service import export_participants_to_excel

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="app/templates")


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    if request.session.get("admin_username"):
        return RedirectResponse(url="/admin/dashboard", status_code=303)
    return templates.TemplateResponse(
        request, "admin_login.html", {"error": None, "event_name": settings.EVENT_NAME}
    )


@router.post("/login", response_class=HTMLResponse)
def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    admin = db.query(Admin).filter(Admin.username == username).first()

    if not admin or not verify_password(password, admin.password_hash):
        return templates.TemplateResponse(
            request,
            "admin_login.html",
            {"error": "Invalid username or password.", "event_name": settings.EVENT_NAME},
            status_code=401,
        )

    request.session["admin_username"] = admin.username
    return RedirectResponse(url="/admin/dashboard", status_code=303)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/admin/login", status_code=303)


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("admin_username"):
        return RedirectResponse(url="/admin/login", status_code=303)

    total = db.query(Participant).count()
    checked_in = db.query(Participant).filter(Participant.checked_in == True).count()  # noqa: E712
    pending = total - checked_in
    recent = db.query(Participant).order_by(Participant.created_at.desc()).limit(10).all()
    men = db.query(Participant).filter(Participant.gender == "male").count()
    women = db.query(Participant).filter(Participant.gender == "female").count()
    recent_men = db.query(Participant).filter(Participant.gender == "male").order_by(Participant.created_at.desc()).limit(10).all()
    recent_women = db.query(Participant).filter(Participant.gender == "female").order_by(Participant.created_at.desc()).limit(10).all()

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "event_name": settings.EVENT_NAME,
            "total": total,
            "checked_in": checked_in,
            "pending": pending,
            "recent": recent,
            "men": men,
            "women": women,
            "recent_men": recent_men,
            "recent_women": recent_women,
        },
    )


@router.get("/export")
def export_excel(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("admin_username"):
        return RedirectResponse(url="/admin/login", status_code=303)

    participants = db.query(Participant).order_by(Participant.created_at.asc()).all()
    excel_file = export_participants_to_excel(participants)

    headers = {"Content-Disposition": "attachment; filename=knm_fitness_participants.xlsx"}
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )
