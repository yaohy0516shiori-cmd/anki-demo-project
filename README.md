# Memory Flashcards

![backend-ci](https://github.com/yaohy0516shiori-cmd/Memory-flashcards/actions/workflows/backend-ci.yml/badge.svg)

Memory Flashcards is a full-stack spaced-repetition flashcard application built with FastAPI, React, TypeScript, PostgreSQL, and Redis. Built as a personal project to explore full-stack architecture, backend testing practices, and spaced-repetition scheduling algorithms.

The project supports user authentication, deck and note management, automatic card generation from note types, study sessions, review logging, learning dashboards, and a backend prototype for AI-assisted card draft generation.

## Tech Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Redis
- PyJWT
- Pytest
- Alembic

### Frontend

- React
- TypeScript
- Vite
- React Router
- ESLint

## Features

- User registration and login
- JWT-based protected API access
- Email verification code workflow for registration
- Password reset workflow with verification code
- Redis-backed verification code TTL and cooldown
- User-scoped decks, notes, cards, study sessions, and review logs
- Default deck creation for new users
- Deck create, update, list, and delete workflows
- Safe deck deletion by moving cards to the default deck
- Note create, update, list, and delete workflows
- Basic, reverse, and cloze note types
- Automatic card generation from notes
- Study session flow:
  - start session
  - fetch next card
  - reveal hint
  - reveal back
  - rate answer
- Simplified spaced-repetition scheduler
- Review log tracking
- Dashboard summary, deck statistics, review trends, due-card forecast, pagination, and search
- React frontend pages for auth, dashboard, decks, notes, cards, study, review logs, and password settings
- Backend AI card draft workflow:
  - generate drafts
  - revise drafts
  - confirm accepted drafts into notes/cards
  - reject or discard drafts

## Project Structure

```text
memory flashcard/
├── backend/                 # FastAPI app, routers, auth, settings, dependencies
├── coreengine/               # Domain logic, repositories, scheduler, storage models
├── frontend/                 # React + TypeScript frontend
├── test/                      # Backend unit and API tests
├── alembic/                    # Database migration setup
├── docker-compose.yml            # PostgreSQL and Redis local services
├── requirements.txt                # Backend dependencies
└── README.md
```

## Backend Setup

Create and activate a Python virtual environment:

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```
pip install --upgrade pip
pip install -r requirements.txt
```

Create a `.env` file from the example:

```
# Windows (PowerShell)
Copy-Item .env.example .env

# macOS / Linux
cp .env.example .env
```

Start PostgreSQL and Redis:

```
docker compose up -d
```

Run database migrations:

```
alembic upgrade head
```

Start the backend server:

```
python -m uvicorn backend.app.main:app --reload
```

Backend URL:

```
http://127.0.0.1:8000
```

Health check:

```
http://127.0.0.1:8000/health
```

Expected response:

```
{
  "ok": true
}
```

## Frontend Setup

Open a new terminal:

```
cd frontend
npm install
```

Create the frontend environment file:

```
# Windows (PowerShell)
Copy-Item .env.example .env

# macOS / Linux
cp .env.example .env
```

Start the frontend dev server:

```
npm run dev
```

Frontend URL:

```
http://localhost:5173
```

## Test and Validation

Run backend tests:

```
python -m pytest -q
```

The backend test suite covers 43 test cases across 11 modules, spanning both API and core-domain layers: authentication/user flow, deck policy, user isolation, note/card flow, study flow, dashboard, AI card factory (API and core), and the Redis-backed email verification code service.

Run frontend lint:

```
cd frontend
npm run lint
```

Run frontend production build:

```
cd frontend
npm run build
```

## Current Status

**Implemented:**

- FastAPI backend API
- PostgreSQL SQLAlchemy models
- Redis verification code service
- React frontend main user flows
- Core spaced-repetition workflow
- Dashboard APIs and frontend dashboard
- Backend AI card draft service and API
- Unit/API test coverage for major backend flows (43 test cases, 11 modules)
- GitHub Actions CI pipeline (Postgres + Redis service containers, migrations, full test suite)

**Known gaps:**

- AI card draft frontend page is not implemented yet
- Alembic migration should be checked/updated for AI draft tables before production use
