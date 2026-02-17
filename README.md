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
    - or after install: `field-assist-bot` (runs indexing first, then starts the bot)

## Windows Terminal / PowerShell usage

- One-time install in your venv:
   - `.\\.venv\\Scripts\\pip.exe install -e .`
- Daily run (index any new/changed docs, then start bot):
   - `.\\.venv\\Scripts\\field-assist-bot.exe`
- Force full re-index before startup:
   - `.\\.venv\\Scripts\\field-assist-bot.exe --force-index`
- Start bot without pre-index step:
   - `.\\.venv\\Scripts\\field-assist-bot.exe --skip-index`
- Index only (no bot start):
   - `.\\.venv\\Scripts\\field-assist-index.exe`
- No-install fallback (works immediately from repo root):
   - `.\\.venv\\Scripts\\python.exe -m src.cli`

## Commands available now

- `/ping`
- `/check_case`, `/case_status`, `/team_cases`, `/request_reopen`
- `/protocol`
- `/progress`, `/team_status`, `/fo_productivity`
- `/assignments`, `/where_is`, `/team_for`
- `/form_version`, `/form_changelog`
- `/announce`, `/morning_briefing`
- `/bot_stats`, `/reload_kb`, `/kb_candidates`, `/promote_candidate`, `/set_version`, `/resolve`, `/escalation_stats`

## Health service

- Run health API: `uvicorn src.health:app --reload --port 8080`
- Check endpoint: `GET http://localhost:8080/health`

## Development checks

- `ruff check .`
- `mypy src`
- `pytest`

## Knowledge indexing (persistent RAG cache)

- On bot startup, the knowledge index is loaded from `KNOWLEDGE_INDEX_CACHE_PATH` when unchanged.
- Only changed/new markdown docs are re-embedded; unchanged docs reuse cached vectors.
- The indexer scans markdown files recursively under `KNOWLEDGE_BASE_PATH` (supports subfolders like `icm_follow_up/`, `scto_docs/`, etc.).
- Protocol answers no longer append a `📚 Sources:` list in user-facing replies.
- While running, the bot periodically scans for newly added `*.md` docs and reindexes only when new files are detected.
- Build/update the cache manually:
   - `python scripts/index_knowledge_base.py`
- Force full re-embedding:
   - `python scripts/index_knowledge_base.py --force`
