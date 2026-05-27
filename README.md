# Memory Flashcards

A full-stack spaced repetition flashcard application built with FastAPI, React, TypeScript, and SQLite.

The project supports user authentication, deck management, note/card generation, study sessions, review logging, and a simplified spaced repetition scheduler.

## Tech Stack

### Backend

- Python
- FastAPI
- SQLite
- PyJWT
- Pytest

### Frontend

- React
- TypeScript
- Vite
- React Router

## Project Structure

```text
memory anki demo/
├── backend/          # FastAPI app, routers, dependencies, auth
├── coreengine/       # Core domain logic: users, decks, notes, cards, study, scheduler
├── database/         # Local SQLite database
├── frontend/         # React + TypeScript frontend
├── readme/           # Design notes and development logs
├── requirements.txt  # Backend Python dependencies
└── README.md         # Project setup guide
```

Backend Setup

Run the following commands from the project root.

1. Create a Python virtual environment
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
2. Install backend dependencies
   pip install --upgrade pip
   pip install -r requirements.txt
3. Start the backend server
   python -m uvicorn backend.app.main:app --reload

The backend will run at:

http://127.0.0.1:8000

Health check:

http://127.0.0.1:8000/health

Expected response:

{
"ok": true
}
Frontend Setup

Open a new terminal and run:

cd frontend
npm install
npm run dev

The frontend will run at:

http://localhost:5173
Frontend Environment Variables

Create a local frontend environment file:

Copy-Item .env.example .env

Example content:

VITE_API_BASE_URL=http://localhost:8000
Run Backend Tests

From the project root:

python -m pytest -q

Or:

python -m pytest -q coreengine/test
Run Frontend Checks

From the frontend directory:

npm run lint
npm run build
Main Features
User registration and login
JWT-based authentication
Email verification code workflow for registration
Password reset workflow
User-scoped decks, notes, cards, review logs, and study sessions
Basic, reverse, and cloze note/card generation
Study session flow: start session, get next card, reveal hint, reveal back, rate answer
Review log tracking
React frontend pages for authentication, decks, notes, study, and review logs
Current Status

The current version is an MVP using SQLite and in-memory verification code storage.

Planned engineering upgrades:

PostgreSQL migration
Redis-backed verification code storage and rate limiting
Docker Compose development environment
AI-assisted flashcard generation
CI checks for backend tests, frontend linting, and frontend build
