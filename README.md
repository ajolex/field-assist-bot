# Field Assist Bot

Field Assist Bot is a Discord assistant for IPA Philippines field operations.

## Current status

MVP foundation across all phases is implemented:

- Slash-command cogs for cases, protocol, progress, assignments, forms, announcements, and admin
- Core services for case management, protocol Q&A, progress, escalation, announcements, and scheduling
- Database initialization and repositories for interactions, escalations, announcements, and reopen requests
- Knowledge-base indexing and retrieval pipeline over `docs/knowledge_base`
- Health endpoint at `/health` via FastAPI app in `src/health.py`

## Quick start

1. Create and activate a Python 3.11+ virtual environment.
2. Install dependencies:
   - `pip install -e .[dev]`
3. Copy `.env.example` to `.env` and fill required values.
4. Run bot:
   - `python -m src.bot`

## Commands available now

- `/ping`
- `/check_case`, `/case_status`, `/team_cases`, `/request_reopen`
- `/protocol`
- `/progress`, `/team_status`, `/fo_productivity`
- `/assignments`, `/where_is`, `/team_for`
- `/form_version`, `/form_changelog`
- `/announce`, `/morning_briefing`
- `/bot_stats`, `/reload_kb`, `/set_version`, `/resolve`, `/escalation_stats`

## Health service

- Run health API: `uvicorn src.health:app --reload --port 8080`
- Check endpoint: `GET http://localhost:8080/health`

## Development checks

- `ruff check .`
- `mypy src`
- `pytest`
