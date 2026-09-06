# CampusCare

**Campus Maintenance & Complaint Management System**

A production-style Flask REST API, with a lightweight web console on top, for
reporting, tracking and resolving campus maintenance issues — broken
equipment, electrical faults, plumbing, Wi‑Fi, hostel and housekeeping
complaints — instead of chasing them through WhatsApp groups.

The REST API is the product. The frontend is a thin client that consumes it;
delete `app/templates`, `app/static`, and `app/routes/main.py` and the API
still runs and answers every request correctly.

---

## 1. Overview

Students file a complaint and receive a ticket ID immediately, no login
required. They can track it, browse the full public queue, and search or
filter by category, building, priority and status. Facilities admins
authenticate with a shared admin key and can triage the queue, move tickets
through a controlled status lifecycle, leave remarks, and remove duplicate or
fake reports.

Every status change is written to an `updates` table, so each complaint
carries a full, timestamped audit trail from "Pending" to "Resolved."

---

## 2. Features

### Student-facing
- Report a complaint (title, description, category, building, room, priority,
  contact details)
- Track a complaint by ticket ID
- Browse the entire complaint queue
- Search by title, description, category, building or room number
- Filter by status, category, priority; sort by newest, oldest or priority
- View full complaint detail with a status timeline

### Admin-facing
- Shared admin-key authentication (`X-Admin-Key` header)
- Dashboard with live counts (total / pending / in progress / resolved)
- Table view of all complaints with search + filters
- Move a complaint through its status lifecycle with a remark
- Edit complaint details (blocked once a complaint is Resolved)
- Delete duplicate or fake complaints

### Backend / API
- Flask application factory + blueprints, no business logic in `app.py`
- SQLAlchemy ORM models — no raw SQL anywhere
- Centralized, JSON-only error handling; stack traces are never exposed
- Field-level validation (required fields, email format, phone format,
  category/building/priority whitelist, title/description length)
- Duplicate-complaint detection on creation
- A strict status state machine: **Pending → In Progress → Resolved**, with
  **Rejected** as an alternate terminal branch from Pending or In Progress
- Resolved complaints cannot be edited or re-resolved
- Full pagination, search and filtering on the list endpoint

---

## 3. Architecture

```
Flask Application Factory (app/__init__.py)
        │
        ├── Blueprints (app/routes/*)      → parse request, call service, shape response
        ├── Services (app/services/*)      → business rules, state machine, queries
        ├── Models (app/models/*)          → SQLAlchemy ORM tables
        ├── Utils (app/utils/*)            → validators, errors, decorators, constants
        ├── Templates (app/templates/*)    → Jinja page shells (no business data)
        └── Static (app/static/*)          → CSS + vanilla JS that call the REST API
```

**Why this shape:** routes stay thin and easy to scan; every business rule
(duplicate detection, valid status transitions, "resolved is locked") lives in
one place in `app/services`, so it can't drift between endpoints; and the
frontend only ever talks to `/api/*`, never touching the database directly.

---

## 4. Folder Structure

```
campuscare/
├── app/
│   ├── __init__.py              # application factory
│   ├── config.py                # Dev / Test / Prod config classes
│   ├── extensions.py            # db, cors instances
│   ├── models/
│   │   ├── __init__.py
│   │   ├── complaint.py         # Complaint model
│   │   └── update.py            # Update model
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── main.py              # HTML page routes
│   │   ├── complaints.py        # /api/complaints...
│   │   ├── updates.py           # /api/updates
│   │   ├── stats.py             # /api/stats
│   │   ├── meta.py              # /api/meta (categories/buildings/etc.)
│   │   └── auth.py              # /api/admin/verify
│   ├── services/
│   │   ├── __init__.py
│   │   ├── complaint_service.py # create/list/update/delete logic
│   │   ├── update_service.py    # status state machine
│   │   └── stats_service.py     # dashboard aggregates
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── constants.py         # categories, buildings, priorities, statuses
│   │   ├── validators.py        # payload validation
│   │   ├── errors.py            # APIError + centralized handlers
│   │   ├── responses.py         # success/error JSON envelopes
│   │   └── decorators.py        # @admin_required
│   ├── templates/                # index, report, track, browse, detail, admin*
│   └── static/
│       ├── css/style.css
│       └── js/                   # api.js, ui.js, + one script per page
├── run.py                        # entry point
├── requirements.txt
├── .env.example
└── README.md
```

---

## 5. Installation

Requires **Python 3.10+**.

```bash
# 1. Clone / unzip the project, then cd into it
cd campuscare

# 2. Create a virtual environment
python -m venv venv

# 3. Activate it
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. (Optional) copy environment config
cp .env.example .env
# edit .env to set your own ADMIN_KEY and SECRET_KEY

# 6. Run the app
python run.py
```

The app starts at **http://127.0.0.1:5000**. The SQLite database
(`campuscare.db`) and all tables are created automatically on first run —
no migration step required.

Default admin key (unless overridden in `.env`): **`admin123`**

---

## 6. Running in VS Code

1. Open the `campuscare` folder in VS Code.
2. Open a terminal (`` Ctrl+` ``) and run the installation steps above.
3. Select the `venv` interpreter: `Ctrl+Shift+P` → **Python: Select
   Interpreter** → choose `./venv/bin/python` (or `.\venv\Scripts\python.exe`
   on Windows).
4. Run `python run.py`, or press `F5` with a basic Flask launch
   configuration.
5. Visit `http://127.0.0.1:5000` in your browser.

---

## 7. REST API Endpoints

All endpoints are prefixed with `/api`. Admin-protected endpoints require the
header `X-Admin-Key: <your admin key>`.

| Method | Endpoint                          | Auth  | Description                                    |
|--------|------------------------------------|-------|------------------------------------------------|
| GET    | `/api/meta`                        | —     | Categories, buildings, priorities, statuses     |
| GET    | `/api/complaints`                  | —     | List complaints (search/filter/sort/paginate)   |
| POST   | `/api/complaints`                  | —     | Report a new complaint                          |
| GET    | `/api/complaints/<id>`             | —     | Fetch one complaint with its update history      |
| PATCH  | `/api/complaints/<id>`             | Admin | Edit complaint fields (blocked if Resolved)      |
| DELETE | `/api/complaints/<id>`             | Admin | Delete a complaint                              |
| GET    | `/api/complaints/<id>/updates`     | —     | Fetch a complaint's audit trail                 |
| POST   | `/api/updates`                     | Admin | Change status + log a remark                    |
| GET    | `/api/stats`                       | —     | Dashboard statistics                            |
| POST   | `/api/admin/verify`                | —     | Verify an admin key                             |

### `GET /api/complaints` query parameters
`status`, `category`, `priority`, `building`, `search`, `sort`
(`newest` \| `oldest` \| `priority`), `page`, `per_page`

### Example: report a complaint

```bash
curl -X POST http://127.0.0.1:5000/api/complaints \
  -H "Content-Type: application/json" \
  -d '{
        "title": "Broken fan in classroom",
        "description": "The ceiling fan in room 204 has not worked since Monday.",
        "category": "Electrical",
        "building": "Academic Block A",
        "room_number": "204",
        "priority": "High",
        "reported_by": "Riya Sharma",
        "email": "riya.sharma@college.edu",
        "phone": "9876543210"
      }'
```

### Example: change status (admin)

```bash
curl -X POST http://127.0.0.1:5000/api/updates \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: admin123" \
  -d '{
        "complaint_id": 1,
        "status": "In Progress",
        "updated_by": "Electrical Dept.",
        "remark": "Technician assigned, visiting tomorrow."
      }'
```

### Response envelope

```json
{
  "success": true,
  "message": "Complaint fetched successfully.",
  "data": { "...": "..." },
  "meta": { "page": 1, "total_items": 12 }
}
```

Errors follow the same shape with `"success": false` and, where relevant, an
`"errors"` array of field-level messages.

### HTTP status codes used
`200` OK · `201` Created · `400` Validation error · `401` Missing/invalid
admin key · `404` Not found · `409` Conflict (duplicate, invalid transition,
editing a resolved ticket) · `500` Unexpected server error (never leaks a
stack trace)

---

## 8. Validation Rules

| Field         | Rule                                                              |
|---------------|--------------------------------------------------------------------|
| `title`       | Required, 5–150 characters                                        |
| `description` | Required, 10–2000 characters                                      |
| `category`    | Required, must be one of the 10 fixed categories                  |
| `building`    | Required, must be one of the fixed building list                  |
| `room_number` | Required, max 20 chars, letters/numbers/hyphens/slashes only      |
| `priority`    | Required, one of `Low` / `Medium` / `High`                        |
| `email`       | Required, valid email format                                      |
| `phone`       | Required, valid 10-digit Indian mobile number                     |
| `reported_by` | Required, max 100 characters                                      |

`PATCH` requests validate only the fields that are actually supplied
(partial validation).

---

## 9. Business Logic

- **Status lifecycle:** `Pending → In Progress → Resolved`, with `Rejected`
  reachable from `Pending` or `In Progress`. `Resolved` and `Rejected` are
  terminal — no further transitions are permitted from either.
- **Resolved complaints are locked:** any `PATCH` to a Resolved complaint
  returns `409 Conflict`.
- **No re-resolving:** applying the same status twice (e.g. resolving an
  already-Resolved ticket) returns `409 Conflict`.
- **Duplicate detection:** creating a complaint with the same title,
  category, building and room as an existing *open* (non-terminal) complaint
  returns `409 Conflict` with the existing ticket's ID, instead of a second
  ticket. Admins can also explicitly mark a complaint `Rejected` with a
  remark such as "Duplicate of #12."
- **Every status change is logged:** `POST /api/updates` writes to the
  `updates` table so complaints always retain a complete history — this is
  intentionally separate from the general-purpose `PATCH` endpoint used for
  correcting details like priority or room number.

---

## 10. Future Scope

*(Mentioned for roadmap purposes only — not implemented in this build.)*

- Photo upload for complaint evidence
- Technician assignment and workload balancing
- AI-based automatic complaint categorization
- Email notifications on status change
- SMS notifications for high-priority tickets
- College SSO / ID-card login integration
- ML-based complaint priority prediction

---

## 11. Tech Stack

| Layer      | Technology                          |
|------------|--------------------------------------|
| Backend    | Python, Flask, Flask-SQLAlchemy, Flask-CORS |
| Database   | SQLite (via SQLAlchemy ORM)          |
| Frontend   | HTML5, CSS3 (custom, no framework), Vanilla JavaScript |

---

Built as a demonstration of REST API architecture, validation, and
business-rule enforcement with Flask — suitable for a college facilities
team to genuinely deploy, or for evaluating backend engineering skills.
