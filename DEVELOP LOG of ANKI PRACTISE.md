# DEVELOP LOG

## 2026-03-05

**-- complete set up git**

**-- using git to push my code to GitHub**

**-- start understanding the framework of ANKI, plan to use python to rebuild it**

## **-- my stack**

| Layer       | Tech                       |
| :---------- | :------------------------- |
| Web UI      | TypeScript + React/Next.js |
| API         | Python FastAPI             |
| DB          | PostgreSQL                 |
| Cache/Queue | Redis                      |
| Worker      | Celery/RQ                  |
| Engine      | Python + Rust              |

## -- basic plan

Phase 1: Core engine (Python only)

Goal: Implement the spaced repetition logic.

- Cards, decks, scheduling algorithm (SM-2 or similar)
- No web UI, no database yet
- Test with Python scripts or a simple CLI

Why first: This is the heart of Anki. Everything else builds on it.

Phase 2: API + simple persistence

Goal: Expose the engine via HTTP and save data.

- FastAPI endpoints (create deck, add card, review card)
- SQLite instead of PostgreSQL (no separate DB server, easier to start)

Why: You learn API design and basic persistence without extra setup.

Phase 3: Basic web UI

Goal: A minimal UI to use the app.

- React/Next.js + TypeScript
- Simple pages: list decks, add cards, review cards

Why: You get a full local app and learn frontend–backend integration.

Phase 4: Move to PostgreSQL

Goal: Use a real database.

- Replace SQLite with PostgreSQL
- Add migrations (e.g. Alembic)

Phase 5: Redis, Celery, Rust (when needed)

Goal: Add these only when you have a concrete need.

- Redis: caching, sessions, rate limiting
- Celery/RQ: background jobs (sync, exports, etc.)
- Rust: performance-critical parts of the engine

What to start with right now

| Do now                                 | Skip for now                  |
| :------------------------------------- | :---------------------------- |
| Python core engine (spaced repetition) | PostgreSQL → use SQLite first |
| FastAPI (simple endpoints)             | Redis, Celery                 |
| Basic React/Next UI                    | Rust                          |
| Local only                             | Deployment                    |