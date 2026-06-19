# KNM Fitness Anakapalle Launch Event — Event Management Web App

A complete production-ready event registration, QR check-in, live dashboard, and lucky-draw system built with FastAPI, PostgreSQL, SQLAlchemy, and Jinja2 + Tailwind CSS.

## Features

- Public landing page and registration form (Name, Age, Weight, City, Phone, Email)
- Unique sequential Registration IDs in the format `KNM-00001`, `KNM-00002`, ...
- QR code generated per participant, encoding `{"reg_id": "KNM-00001"}`
- PostgreSQL database via SQLAlchemy ORM
- Secure admin login + dashboard (Total / Checked-In / Pending stat cards, recent registrations table)
- Live dashboard stats via AJAX polling (no page refresh)
- Camera-based QR check-in page (uses the device camera in the browser) with manual lookup fallback
- Lucky Draw page: random winner selection among checked-in, non-winning participants, with winner history
- One-click Excel export of all participant data
- Black / White / Gold modern, responsive UI (mobile, tablet, desktop)

## Project Structure

```
knm_fitness_event/
├── requirements.txt
├── .env.example
├── README.md
└── app/
    ├── main.py                  # FastAPI app, startup (tables, sequence, admin seed)
    ├── config.py                 # Settings loaded from .env
    ├── database.py                # SQLAlchemy engine/session
    ├── models.py                  # Participant, Admin models + reg_id sequence
    ├── schemas.py                 # Pydantic request/response schemas
    ├── auth.py                    # Password hashing + admin auth dependency
    ├── routes/
    │   ├── public.py              # Home, Register, Success
    │   ├── admin.py                # Admin login/logout, dashboard, Excel export
    │   ├── checkin.py              # QR check-in page + APIs
    │   ├── lucky_draw.py           # Lucky draw page + pick-winner API
    │   └── api.py                  # /api/stats for live dashboard polling
    ├── services/
    │   ├── qr_service.py            # QR code generation
    │   ├── excel_service.py         # Excel export
    │   └── lucky_draw_service.py    # Winner selection logic
    ├── utils/
    │   └── id_generator.py          # Sequential KNM-00001 style reg_id generator
    ├── templates/                  # Jinja2 + Tailwind HTML templates
    └── static/
        ├── css/custom.css
        ├── js/dashboard.js
        ├── js/checkin.js
        ├── js/lucky_draw.js
        └── qrcodes/                # Generated QR PNGs are saved here
```

## Prerequisites

- Python 3.10+
- PostgreSQL 13+ (running locally or accessible remotely)

## Setup Instructions

### 1. Clone / unzip the project and enter the folder

```bash
cd knm_fitness_event
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the PostgreSQL database

```bash
psql -U postgres -c "CREATE DATABASE knm_fitness;"
```

(Adjust the username/host as needed for your PostgreSQL setup.)

### 5. Configure environment variables

Copy the example file and edit it:

```bash
cp .env.example .env
```

Edit `.env`:

```
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/knm_fitness
SECRET_KEY=replace-with-a-long-random-secret-key
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
EVENT_NAME=KNM Fitness Anakapalle Launch Event
EVENT_DATE=2026-07-15
EVENT_LOCATION=Anakapalle, Andhra Pradesh
EVENT_DESCRIPTION=Join us for the grand launch of KNM Fitness — a celebration of strength, health and community.
```

> The admin account is auto-created on first startup using `ADMIN_USERNAME` / `ADMIN_PASSWORD` if no admin exists yet. **Change the default password before deploying to production.**

## Run Instructions

```bash
uvicorn app.main:app --reload
```

The app will be available at: `http://127.0.0.1:8000`

On first run, the app automatically:
- Creates all database tables
- Creates the `reg_id_seq` PostgreSQL sequence used for `KNM-00001`-style IDs
- Seeds the default admin account (if one doesn't already exist)

## Key Pages

| Page | URL |
|---|---|
| Home | `/` |
| Register | `/register` |
| Registration Success | `/success/{reg_id}` |
| Admin Login | `/admin/login` |
| Admin Dashboard | `/admin/dashboard` |
| QR Check-In | `/checkin` |
| Lucky Draw | `/lucky-draw` |
| Excel Export | `/admin/export` |
| Health Check | `/health` |

## Notes on the QR Check-In Camera

The check-in page uses the `html5-qrcode` JS library (loaded via CDN) to access the device camera directly in the browser — no native app required. Most browsers require **HTTPS** (or `localhost`) to grant camera access, so when deploying beyond local testing, serve the app over HTTPS or use a reverse proxy (e.g. Nginx + Let's Encrypt) in front of it. A manual Registration ID lookup field is also provided as a fallback if camera access isn't available.

## Production Notes

- Change `ADMIN_PASSWORD` and `SECRET_KEY` in `.env` before deploying.
- Consider running behind Gunicorn + Uvicorn workers, or a process manager such as systemd/Supervisor, with Nginx as a reverse proxy.
- Back up the PostgreSQL database regularly, especially around the live event.
