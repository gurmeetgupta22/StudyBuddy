# StudyBuddy — AI-Powered Learning Platform

A full-stack web application that generates AI study notes, creates custom tests, and tracks learning progress. Built with FastAPI and vanilla JavaScript.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+, FastAPI, Uvicorn |
| Database | SQLAlchemy (async) + PostgreSQL / SQLite |
| Auth | Google OAuth 2.0 + JWT (python-jose) |
| AI | OpenRouter API (Llama 3.1 8B) |
| PDF | ReportLab |
| Frontend | Vanilla JS, CSS custom properties |
| Rate Limiting | SlowAPI |

---

## Features

- Google OAuth 2.0 login with JWT session management
- Onboarding survey (school / college / other)
- AI-generated study notes with 9 structured sections
- Interactive MCQ tests with instant scoring and feedback
- Configurable test generation (sections, question types, difficulty)
- Accuracy tracking and analytics dashboard
- Bar chart accuracy trend, weak area detection
- PDF export for notes and test papers (with/without answers)
- Bookmarking and full searchable history
- Dark / light theme
- Voice input for note topics
- Fully responsive (mobile + desktop)
- Rate-limited API

---

## Project Structure

```
StudyBuddy/
├── main.py                          # FastAPI entry point
├── requirements.txt
├── .env                             # Environment variables
├── backend/
│   ├── config.py                    # Pydantic settings
│   ├── database.py                  # SQLAlchemy async engine
│   ├── models/models.py             # ORM models
│   ├── schemas/schemas.py           # Pydantic schemas
│   ├── routes/
│   │   ├── auth.py                  # Google OAuth + JWT
│   │   ├── user.py                  # Profile + survey
│   │   ├── notes.py                 # Notes CRUD
│   │   ├── test.py                  # Test generation & scoring
│   │   ├── analytics.py             # Learning analytics
│   │   ├── execute.py               # Code execution
│   │   └── export.py                # PDF export
│   ├── services/
│   │   ├── ai_service.py            # OpenRouter LLM calls
│   │   └── pdf_service.py           # ReportLab PDF generation
│   └── utils/
│       ├── jwt_handler.py           # JWT encode / decode
│       └── dependencies.py          # Auth dependency
└── frontend/
    ├── index.html                   # Landing page
    ├── styles/main.css              # Design system
    ├── scripts/
    │   ├── routes.js                # URL slug mapping
    │   ├── api.js                   # API client
    │   ├── sidebar.js               # Navigation + theme
    │   └── utils.js                 # UI helpers
    └── pages/                       # Randomized slug filenames
        ├── a8xQ3m.html              # Dashboard
        ├── k7pR2n.html              # Study Notes
        ├── x9mB4v.html              # Tests
        ├── j3nK8w.html              # Survey
        ├── t5Lp1d.html              # History
        ├── c6rS9z.html              # Analytics
        └── f2gH7q.html              # Auth callback
```

---

## Local Development

### Prerequisites

- Python 3.11+
- pip

### Setup

```bash
python -m venv venv
source venv/bin/activate     # Linux/macOS
.\venv\Scripts\activate.ps1  # Windows

pip install -r requirements.txt
```

### Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

| Variable | Description | Required |
|---|---|---|
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | Yes |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | Yes |
| `GOOGLE_REDIRECT_URI` | `http://localhost:8000/auth/google/callback` | Yes |
| `OPENROUTER_API_KEY` | OpenRouter API key for AI calls | Yes |
| `JWT_SECRET_KEY` | Random 32+ character string | Yes |
| `FRONTEND_URL` | `http://localhost:8000` | Yes |
| `DATABASE_URL` | `sqlite:///./studybuddy.db` (default) | No |

### Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → Credentials
2. Create an OAuth 2.0 Client ID (Web application)
3. Add **Authorized redirect URI**: `http://localhost:8000/auth/google/callback`
4. Add **Authorized JavaScript origin**: `http://localhost:8000`

### Run

```bash
python main.py
```

Open `http://localhost:8000` in your browser.

---

## Deploy to Render

### 1. PostgreSQL Database

- Create a new **PostgreSQL** instance on Render
- Copy the **Internal Database String**
- Add `+asyncpg` to the scheme: `postgresql+asyncpg://user:password@host:5432/dbname`

### 2. Web Service

- Create a new **Web Service** connected to your GitHub repository
- **Runtime**: Python 3.11
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 3. Environment Variables

Set these in the Render dashboard:

| Variable | Value |
|---|---|
| `APP_ENV` | `production` |
| `FRONTEND_URL` | `https://your-app.onrender.com` |
| `JWT_SECRET_KEY` | Random 32+ character string |
| `DATABASE_URL` | `postgresql+asyncpg://...` (Render Postgres) |
| `GOOGLE_CLIENT_ID` | From Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | From Google Cloud Console |
| `GOOGLE_REDIRECT_URI` | `https://your-app.onrender.com/auth/google/callback` |
| `OPENROUTER_API_KEY` | Your OpenRouter key |

### 4. Update Google Cloud Console

Add to your OAuth client:
- **Authorized redirect URI**: `https://your-app.onrender.com/auth/google/callback`
- **Authorized JavaScript origin**: `https://your-app.onrender.com`

---

## API Endpoints

### Auth
| Method | Endpoint | Description |
|---|---|---|
| GET | `/auth/google/login` | Redirect to Google consent screen |
| GET | `/auth/google/callback` | OAuth callback (exchanges code for JWT) |
| POST | `/auth/exchange` | Alternative — exchange auth code via JSON |

### User
| Method | Endpoint | Description |
|---|---|---|
| GET | `/user/me` | Get current user profile |
| POST | `/user/survey` | Submit onboarding survey |

### Notes
| Method | Endpoint | Description |
|---|---|---|
| POST | `/notes/generate` | Generate AI study notes |
| GET | `/notes/` | List all notes |
| GET | `/notes/{id}` | Get note by ID |
| DELETE | `/notes/{id}` | Delete a note |
| POST | `/notes/{id}/bookmark` | Toggle bookmark |

### Tests
| Method | Endpoint | Description |
|---|---|---|
| POST | `/test/generate` | Generate AI test |
| GET | `/test/` | List all tests |
| GET | `/test/{id}` | Get test by ID |
| POST | `/test/score` | Submit MCQ answers and get score |
| DELETE | `/test/{id}` | Delete a test |

### Analytics
| Method | Endpoint | Description |
|---|---|---|
| GET | `/analytics/` | Get learning analytics |

### Export
| Method | Endpoint | Description |
|---|---|---|
| GET | `/export/notes/{id}/pdf` | Export note as PDF |
| GET | `/export/test/{id}/pdf` | Export test as PDF |

### System
| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/api/docs` | Swagger UI |
| GET | `/api/redoc` | ReDoc UI |

---

## Security

- All data endpoints are JWT-protected via bearer token
- API keys and secrets are loaded from environment variables only
- Input validation via Pydantic schemas
- CORS restricted to the configured frontend origin
- Rate limiting on all API routes via SlowAPI
- Page URLs use randomized slugs to prevent trivial enumeration
