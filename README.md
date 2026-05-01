# MedNotice API

MedNotice is a healthcare system that streamlines how patients book and manage medical appointments while ensuring trust and reliability in the system. It allows patients to schedule, reschedule, and cancel appointments with doctors, while doctors can manage their availability and interactions with patients.

A key problem MedNotice solves is lack of trust and coordination in healthcare access, especially in environments where verifying qualified professionals is critical. The system introduces a doctor verification and approval workflow, ensuring that only vetted doctors can receive appointments. It also improves communication through automated email notifications and reminders powered by background tasks, helping reduce missed appointments and improve patient engagement.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Django](https://img.shields.io/badge/Django-5.x-green)
![DRF](https://img.shields.io/badge/DRF-3.x-red)
![Celery](https://img.shields.io/badge/Celery-5.x-brightgreen)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-blue)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)

---

## Table of Contents

- [Project Overview](#project-overview)
- [Entity Relationship Diagram](#entity-relationship-diagram)
- [Design Decisions](#design-decisions)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
  - [Database Setup](#database-setup)
- [Running the App](#running-the-app)
- [Health Check](#health-check)
- [API Overview](#api-overview)
- [Known Limitations](#known-limitations)
- [Project Structure](#project-structure)

---

## Project Overview

MedNotice is a backend API for managing healthcare appointments between patients and doctors. It supports three user roles — **Patient**, **Doctor**, and **Admin** — each with distinct workflows and permissions.

**Core features include:**

- Patient self-registration and doctor-invite-based onboarding
- Doctor verification by admin before platform access is granted
- Appointment request flow where patients book and doctors accept or decline
- Doctor shift scheduling to define availability and time slots
- Automated email notifications for all appointment lifecycle events
- Appointment reminders via Celery Beat scheduled tasks
- JWT-based authentication with token refresh and blacklisting
- Password reset and email verification flows
- Full admin management panel

---

## Entity Relationship Diagram

```
┌─────────────────┐         ┌─────────────────┐
│   CustomUser    │         │     Patient      │
│─────────────────│         │─────────────────-│
│ id              │ 1     1 │ id               │
│ email           │─────────│ user (FK)        │
│ user_type       │         │ patient_code     │
│ is_active       │         │ first_name       │
│ is_verified     │         │ last_name        │
│ is_staff        │         │ phone_number     │
└─────────────────┘         │ date_of_birth    │
         │                  │ blood_type       │
         │ 1             1  │ allergies        │
         │                  │ chronic_cond..   │
┌────────┴────────┐         └────────┬─────────┘
│     Doctor      │                  │
│─────────────────│                  │
│ id              │                  │ 1
│ user (FK)       │                  │
│ doctor_code     │         ┌────────┴──────────┐
│ first_name      │         │   Appointment     │
│ last_name       │         │───────────────────│
│ specialization  │ 1     * │ id                │
│ years_exp       │─────────│ patient (FK)      │
│ consult_fee     │         │ doctor (FK)       │
│ is_available    │         │ scheduled_time    │
└────────┬────────┘         │ status            │
         │                  │ description       │
         │ 1                │ cancellation_rsn  │
         │                  │ decline_reason    │
┌────────┴────────┐         │ reminder_sent     │
│  DoctorShift    │         │ created_at        │
│─────────────────│         └───────────────────┘
│ id              │
│ doctor (FK)     │
│ day_of_week     │
│ start_time      │
│ end_time        │
│ slot_duration   │
└─────────────────┘
```

**Appointment Status Flow:**

```
PENDING ──► SCHEDULED ──► COMPLETED
   │              │
   ▼              ▼
DECLINED      CANCELLED
```

---

## Design Decisions

### 1. Separate Registration Paths
Public registration is restricted to patients only. Doctors are onboarded via admin invites with a secure one-time password setup link. This eliminates role escalation vulnerabilities where users could register as admins.

### 2. Doctor Verification Gate
Doctors start with `is_verified=False` after accepting their invite. They can log in but cannot perform any actions until an admin explicitly approves their account. This ensures all practicing doctors on the platform are vetted.

### 3. Appointment Request Flow
Patients submit appointment **requests** (status: `PENDING`) rather than directly booking confirmed slots. Doctors then accept or decline. This reflects real-world clinical workflows where doctors control their schedule.

### 4. Shift-Based Availability
Doctors define weekly shifts with start/end times and slot durations. The system generates available slots dynamically and prevents double-booking by checking existing `PENDING` and `SCHEDULED` appointments against requested times.

### 5. Celery for Async Email
All email sending is handled asynchronously via Celery tasks with a retry mechanism (max 3 retries, 60-second countdown). This keeps API response times fast and makes the system resilient to transient email provider failures.

### 6. Celery Beat for Reminders
Appointment reminders are sent via a scheduled Celery Beat task that runs every day at 8AM. A `reminder_sent` flag on the `Appointment` model prevents duplicate reminder emails.

### 7. Single Settings File
Rather than splitting settings into multiple files, the project uses a single `settings.py` driven entirely by environment variables. A `if not DEBUG` block at the bottom activates production security settings automatically when `DEBUG=False`.

### 8. JWT Authentication
SimpleJWT is used with short-lived access tokens (30 minutes) and rotating refresh tokens (1 day) with blacklisting enabled. This balances security with usability.

---

## Getting Started

### Prerequisites

Make sure you have the following installed:

| Tool | Version |
|------|---------|
| Python | 3.12+ |
| Docker | Latest |
| Docker Compose | Latest |
| Poetry | 1.7.1 |
| Git | Latest |

### Installation

**1. Clone the repository:**
```bash
git clone https://github.com/yourusername/mednotice.git
cd mednotice
```

**2. Copy the environment file:**
```bash
cp .env.example .env
```

**3. Fill in your environment variables** (see [Environment Variables](#environment-variables) below)

**4. Build and start the containers:**
```bash
docker compose up --build
```

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
POSTGRES_DB=mednotice
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# Email (SendGrid)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
SENDGRID_API_KEY=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

> **Note:** For local development set `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend` to print emails to the console instead of sending them.

### Database Setup

Migrations run automatically when the containers start. To run them manually:

```bash
docker exec -it mednotice_api python manage.py migrate
```

**Create an admin user:**
```bash
docker exec -it mednotice_api python manage.py create_admin --email admin@example.com --password yourpassword
```

---

## Running the App

**Start all services:**
```bash
docker compose up
```

**Start in detached mode:**
```bash
docker compose up -d
```

**Stop all services:**
```bash
docker compose down
```

**View logs:**
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f api
docker compose logs -f celery
docker compose logs -f celery-beat
```

**Run tests:**
```bash
docker exec -it mednotice_api python manage.py test
```

**Trigger a Celery task manually (for testing):**
```bash
docker exec -it mednotice_api python manage.py shell
```
```python
from notification.tasks import send_appointment_reminder_task
send_appointment_reminder_task.apply()
```

The following services will be running:

| Service | URL |
|---------|-----|
| API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/api/v1/docs/ |
| Django Admin | http://localhost:8000/admin/ |
| Flower (Celery Monitor) | http://localhost:5555 |

---

## Health Check

```
GET /api/v1/health/
```

**Response:**
```json
{
  "status": "ok"
}
```

Use this endpoint to verify the API is running. It is also used by Railway/Render as the deployment health check.

---

## API Overview

### Authentication

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/api/v1/accounts/register/` | Patient registration | Public |
| POST | `/api/v1/accounts/auth/login/` | Login (returns JWT) | Public |
| POST | `/api/v1/accounts/auth/token/refresh/` | Refresh access token | Public |
| POST | `/api/v1/accounts/auth/verify-email/` | Verify email address | Public |
| POST | `/api/v1/accounts/password-reset/` | Request password reset | Public |
| POST | `/api/v1/accounts/password-reset-confirm/` | Confirm password reset | Public |
| POST | `/api/v1/accounts/auth/set-password/` | Set password via invite | Public |

### Admin

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/api/v1/accounts/staff/onboard/` | Invite doctor or admin | Admin |
| POST | `/api/v1/accounts/admin/approve-doctor/` | Approve a doctor account | Admin |
| GET | `/api/v1/appointments/admin/appointments/` | View all appointments | Admin |

### Patient

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/api/v1/patients/patient-profile/` | Create patient profile | Patient |
| GET | `/api/v1/patients/get-patient-profile/` | Get patient profile | Patient |
| PATCH | `/api/v1/patients/update-profile/` | Update patient profile | Patient |
| GET | `/api/v1/patients/dashboard/` | Patient dashboard + history | Patient |
| GET | `/api/v1/appointments/patient/appointments/available-slots/` | Get doctor available slots | Patient |
| POST | `/api/v1/appointments/patient/appointments/` | Book appointment request | Patient |
| POST | `/api/v1/appointments/patient/appointments/{id}/cancel-appointment/` | Cancel appointment | Patient |
| POST | `/api/v1/appointments/patient/appointments/{id}/reschedule/` | Reschedule appointment | Patient |

### Doctor

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/api/v1/doctor/doctor-profile/` | Create doctor profile | Verified Doctor |
| GET | `/api/v1/doctor/get-doctor-profile/` | Get doctor profile | Verified Doctor |
| PATCH | `/api/v1/doctor/update-profile/` | Update doctor profile | Verified Doctor |
| GET | `/api/v1/doctor/dashboard/` | Doctor dashboard + history | Verified Doctor |
| POST | `/api/v1/doctor/shifts/` | Create availability shift | Verified Doctor |
| GET | `/api/v1/doctor/shifts/` | List shifts | Verified Doctor |
| POST | `/api/v1/appointments/doctor/appointments/` | Create appointment | Verified Doctor |
| POST | `/api/v1/appointments/doctor/appointments/{id}/accept/` | Accept appointment request | Verified Doctor |
| POST | `/api/v1/appointments/doctor/appointments/{id}/decline/` | Decline appointment request | Verified Doctor |
| POST | `/api/v1/appointments/doctor/appointments/{id}/cancel-appointment/` | Cancel appointment | Verified Doctor |

### Available Slot Query Example

```
GET /api/v1/appointments/patient/appointments/available-slots/?doctor_code=DOC-12345&date=2026-05-01
```

```json
{
  "doctor_code": "DOC-12345",
  "date": "2026-05-01",
  "available_slots": ["09:00", "09:30", "10:00", "10:30", "11:00"]
}
```

---

## Known Limitations

1. **No payment integration** — consultation fees are stored but there is no payment processing flow implemented yet.

2. **Single timezone** — all appointment times are stored and displayed in UTC. There is no per-user timezone support.

3. **No file uploads** — doctors cannot upload documents, prescriptions, or profile pictures.

4. **No real-time notifications** — notifications are email-only. There is no WebSocket or push notification support.

5. **Single shift per day** — the `DoctorShift` model enforces one shift per doctor per day. Split shifts (e.g. 9AM-12PM and 2PM-5PM) are not supported.

6. **No appointment search or filtering** — the appointment list endpoints return all records without advanced filtering by date range, status, or doctor/patient name.

7. **Free tier limitations** — when deployed on Railway's free tier, services may be limited by the $5 monthly credit. High traffic will exhaust the free allowance.

8. **No soft delete** — cancelling or declining an appointment updates its status but the record is never removed from the database.

---

## Project Structure

```
mednotice/
├── app/                          # Django application root
│   ├── accounts/                 # Authentication, registration, user management
│   │   ├── management/
│   │   │   └── commands/
│   │   │       └── create_admin.py
│   │   ├── enums.py
│   │   ├── models.py             # CustomUser model
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   │
│   ├── appointments/             # Appointment booking and management
│   │   ├── services/
│   │   │   └── scheduling.py     # Slot availability logic
│   │   ├── enums.py
│   │   ├── models.py
│   │   ├── permissions.py
│   │   ├── serializer.py
│   │   ├── urls.py
│   │   └── views.py
│   │
│   ├── common/                   # Shared utilities and base classes
│   │
│   ├── core/                     # Django project configuration
│   │   ├── celery.py             # Celery app configuration
│   │   ├── pagination.py
│   │   ├── settings.py           # Single settings file
│   │   ├── urls.py
│   │   └── wsgi.py
│   │
│   ├── doctor/                   # Doctor profiles and shift management
│   │   ├── models.py             # Doctor, DoctorShift models
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   │
│   ├── notification/             # Email notifications
│   │   ├── services.py           # EmailService class
│   │   ├── tasks.py              # Celery tasks
│   │   └── templates/
│   │       └── emails/           # HTML email templates
│   │           ├── base.html
│   │           ├── appointment_accepted.html
│   │           ├── appointment_cancelled.html
│   │           ├── appointment_created_patient.html
│   │           ├── appointment_declined.html
│   │           ├── appointment_reminder.html
│   │           ├── appointment_request_doctor.html
│   │           ├── appointment_reschedule.html
│   │           ├── doctor_approved.html
│   │           ├── password_reset.html
│   │           ├── staff_invite.html
│   │           └── verify_email.html
│   │
│   ├── patients/                 # Patient profiles and dashboard
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   │
│   └── manage.py
│
├── docker/
│   ├── dev/
│   │   └── Dockerfile            # Development Dockerfile
│   └── prod/
│       └── Dockerfile            # Production Dockerfile
│
├── .env.example                  # Example environment variables
├── .gitignore
├── docker-compose.yml            # Local development services
├── pyproject.toml                # Poetry dependencies
└── README.md
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Django 5.x + Django REST Framework |
| Authentication | SimpleJWT |
| Task Queue | Celery + Redis |
| Task Scheduler | Celery Beat + django-celery-beat |
| Database | PostgreSQL 14 |
| Email | SendGrid |
| API Documentation | drf-spectacular (Swagger UI) |
| Containerisation | Docker + Docker Compose |
| Deployment | Railway |
| Dependency Management | Poetry |

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License.
