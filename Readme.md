
# Clinic Management App

A simple clinic management system built with FastAPI and Streamlit.

## Tech Stack

- FastAPI (backend API)
- Streamlit (frontend/dashboard)
- SQLite
- SQLAlchemy
- Pydantic
- Git + GitHub

## Project Structure
```
clinic/
├── backend/
│   ├── main.py         # FastAPI app and routes
│   ├── models.py       # SQLAlchemy database models
│   ├── schemas.py      # Pydantic request/response schemas
│   ├── database.py     # Database connection and session
│   └── .env            # Environment variables (not committed)
├── frontend/
│   ├── CliniC.py       # Dashboard (entry point)
│   ├── api.py          # API call functions
│   └── pages/
│       ├── 1_Patients.py
│       └── 2_Appointments.py
├── requirements.txt
└── README.md
```
## Features

- **Patient Management** — add, view, search, edit, delete
- **Appointment Management** — create, filter by date/status, mark as complete
- **Dashboard** — live patient count, today's appointments, upcoming list
- **CSV Export** — download all patients as a CSV file
- **Dark Mode** — built into Streamlit, toggle from the settings menu

## Setup

**1. Clone the repository:**

```bash
git clone https://github.com/yourusername/clinic.git
cd clinic
```

**2. Create the `.env` file inside `/backend`:**

DATABASE_URL=sqlite:///./clinic.db

## Running the App

### Option 1 — Docker (Recommended)

Make sure Docker Desktop is running, then from the project root:

```bash
docker-compose up --build
```

Open `http://localhost:8501` in your browser.

To stop:

```bash
docker-compose down
```

### Option 2 — Without Docker

**1. Create and activate virtual environment:**

```bash
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Windows Command Prompt
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

**2. Install dependencies:**

```bash
cd backend
pip install -r requirements.txt

cd ../frontend
pip install -r requirements.txt
```

**3. Two terminals needed, both with the virtual environment activated:**

Terminal 1 — Backend:
```bash
cd backend
uvicorn main:app --reload
```

Terminal 2 — Frontend:
```bash
cd frontend
streamlit run CliniC.py
```

Open `http://localhost:8501` in your browser.

## API Documentation

FastAPI generates interactive API docs automatically.
Open `http://127.0.0.1:8000/docs` after starting the backend.

### Patients

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/patients` | Get all patients |
| GET | `/patients?search=name` | Search patients by name |
| POST   | `/patients` | Create a new patient |
| PUT    | `/patients/{id}` | Update a patient |
| DELETE | `/patients/{id}` | Delete a patient |

### Appointments

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/appointments` | Get all appointments |
| GET    | `/appointments?date=2025-05-15` | Filter by date |
| GET    | `/appointments?status=Scheduled` | Filter by status |
| POST   | `/appointments` | Create a new appointment |
| PUT    | `/appointments/{id}` | Update an appointment |
| DELETE | `/appointments/{id}` | Delete an appointment |

### Example — Create Patient

```json
POST /patients
{
    "name": "Aisha Nair",
    "age": 28,
    "gender": "Female",
    "phone": "9876543210",
    "symptoms": "Fever, headache"
}
```

### Example — Create Appointment

```json
POST /appointments
{
    "patient_id": 1,
    "doctor": "Dr. Mehta",
    "date": "2025-05-15",
    "time": "10:00 AM",
    "status": "Scheduled"
}
```

## for Dark Mode ( streamlit already has a darkmode feature in-built)

1. Open the app in your browser
2. Click the **⋮** menu in the top right corner
3. Select **Settings**
4. Toggle **Dark mode**