"""
Public-facing routes: landing page, registration form, success page.
No authentication required -- this is the part the general public uses.
"""

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Participant
from app.schemas import ParticipantCreate
from app.services.qr_service import generate_qr_code
from app.utils.id_generator import generate_reg_id
from app.utils.email_service import EmailDeliveryError, send_registration_email
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _event_context(request: Request) -> dict:
    return {
        "request": request,
        "event_name": settings.EVENT_NAME,
        "event_date": settings.EVENT_DATE,
        "event_location": settings.EVENT_LOCATION,
        "event_description": settings.EVENT_DESCRIPTION,
    }


def _store_registration_success(request: Request, participant: Participant | dict) -> None:
    if isinstance(participant, dict):
        payload = participant
    else:
        payload = {
            "reg_id": participant.reg_id,
            "name": participant.name,
            "message": "Your QR code has been sent to your email address.",
            "qr_path": participant.qr_path,
        }

    request.session["registration_success"] = payload


def _consume_registration_success(request: Request) -> dict | None:
    success_data = request.session.pop("registration_success", None)
    if isinstance(success_data, dict):
        return success_data
    return None


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    context = _event_context(request)
    context["registration_success"] = _consume_registration_success(request)
    return templates.TemplateResponse(request, "index.html", context)


@router.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    context = _event_context(request)
    context["errors"] = {}
    context["form_data"] = {}
    return templates.TemplateResponse(request, "register.html", context)


@router.post("/register", response_class=HTMLResponse)
async def register_submit(
    request: Request,
    name: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    city: str = Form(...),
    gender: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    instagram_followed: bool = Form(...),
    db: Session = Depends(get_db),
):
    form_data = {
        "name": name,
        "age": age,
        "weight": weight,
        "city": city,
        "gender": gender,
        "phone": phone,
        "email": email,
        "instagram_followed": instagram_followed,
    }
    errors: dict = {}

    # --- Field-level validation -----------------------------------------
    try:
        validated = ParticipantCreate(**form_data)
    except ValidationError as exc:
        for err in exc.errors():
            field = str(err["loc"][0])
            errors[field] = err["msg"]

        context = _event_context(request)
        context["errors"] = errors
        context["form_data"] = form_data
        return templates.TemplateResponse(request, "register.html", context, status_code=400)

    # --- Uniqueness checks (phone + email) -------------------------------
    if db.query(Participant).filter(Participant.phone == validated.phone).first():
        errors["phone"] = "This phone number is already registered."

    if db.query(Participant).filter(Participant.email == validated.email).first():
        errors["email"] = "This email address is already registered."

    if errors:
        context = _event_context(request)
        context["errors"] = errors
        context["form_data"] = form_data
        return templates.TemplateResponse(request, "register.html", context, status_code=400)

    # --- Create participant ------------------------------------------------
    reg_id = generate_reg_id(db)

    participant = Participant(
        reg_id=reg_id,
        name=validated.name,
        age=validated.age,
        weight=validated.weight,
        city=validated.city,
        gender=validated.gender,
        phone=validated.phone,
        email=validated.email,
    )
    db.add(participant)
    db.commit()
    db.refresh(participant)

    # --- Generate + attach QR code ------------------------------------------
    qr_web_path, qr_file_path = generate_qr_code(reg_id)
    participant.qr_path = qr_web_path
    db.commit()

    try:
        await send_registration_email(
            participant.email,
            participant.name,
            qr_file_path,
            phone_number=participant.phone,
        )
    except EmailDeliveryError:
        # Keep registration successful even if email delivery fails.
        pass

    _store_registration_success(request, participant)
    return RedirectResponse(url="/", status_code=303)


@router.get("/success/{reg_id}", response_class=HTMLResponse)
def success_page(request: Request, reg_id: str, db: Session = Depends(get_db)):
    participant = db.query(Participant).filter(Participant.reg_id == reg_id).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Registration not found")

    context = _event_context(request)
    context["participant"] = participant
    return templates.TemplateResponse(request, "success.html", context)
