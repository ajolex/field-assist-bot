# Field Assist Bot Onboarding

## 1) Quick setup checklist

- Clone this repo and open it in VS Code.
- Create `.env` from `.env.example`.
- Fill Discord, SurveyCTO, Google Sheets, and Stata values.
- Confirm your bot has `applications.commands` and `bot` scopes in the target server.
- Confirm the bot can send messages in your configured channels.

## 2) Required environment values

Minimum required for production flow:

- `DISCORD_BOT_TOKEN`
- `DISCORD_GUILD_IDS`
- `GOOGLE_SERVICE_ACCOUNT_JSON`
- `GOOGLE_ASSIGNMENTS_SHEET_ID`
- `GOOGLE_PRODUCTIVITY_SHEET_ID`
- `GOOGLE_FORM_HH_SURVEY_SHEET_ID`
- `GOOGLE_FORM_ICM_BUSINESS_SHEET_ID`
- `SURVEYCTO_SERVER_NAME`
- `SURVEYCTO_USERNAME`
- `SURVEYCTO_PASSWORD`
- `STATA_EXECUTABLE`
- `SURVEYCTO_FORM_HOUSEHOLD_ID`
- `SURVEYCTO_FORM_BUSINESS_ID`
- `SURVEYCTO_HOUSEHOLD_CSV_PATH`
- `SURVEYCTO_BUSINESS_CSV_PATH`
- `STATA_HOUSEHOLD_MASTER_DO_PATH`
- `STATA_BUSINESS_MASTER_DO_PATH`

Date filter for automation downloads:

- `SURVEYCTO_SCTOAPI_DATE=1756051200`
  - This is August 25, 2025 00:00 (Asia/Manila).
  - Change this value in `.env` when you need a different start date.

## 3) Run commands (Windows / PowerShell)

Install once in virtual environment:

- `.\.venv\Scripts\pip.exe install -e .[dev]`

Start bot (recommended):

- `.\.venv\Scripts\field-assist-bot.exe`

Start bot without pre-index:

- `.\.venv\Scripts\field-assist-bot.exe --skip-index`

Force full index before startup:

- `.\.venv\Scripts\field-assist-bot.exe --force-index`

Index only:

- `.\.venv\Scripts\field-assist-index.exe`

Fallback startup (no install entrypoint):

- `.\.venv\Scripts\python.exe -m src.cli`

## 4) Discord command guide

Core command groups:

- Cases: `/check_case`, `/case_status`, `/team_cases`, `/request_reopen`
- Protocol: `/protocol`
- Progress: `/progress`, `/team_status`, `/fo_productivity`
- Assignments: `/assignments`, `/where_is`, `/team_for`
- Forms: `/form_version`, `/form_changelog`
- Announcements: `/announce`, `/morning_briefing`
- Admin: `/bot_stats`, `/reload_kb`, `/kb_candidates`, `/promote_candidate`, `/set_version`, `/resolve`, `/escalation_stats`
- Issue triage: message context menu `Create Field Issue`, plus `/issue_update`, `/issue_show`
- Automation: `/run_job`

## 5) Automation jobs

Current whitelisted job:

- `scto_dms_daily`

How to run from Discord:

- `/run_job` then choose `scto_dms_daily`

What this job does:

- Runs official SurveyCTO Stata command `sctoapi` for HH and Business forms.
- Applies `date(SURVEYCTO_SCTOAPI_DATE)` filter from `.env`.
- Ensures preferred CSV outputs are available at:
  - `SURVEYCTO_HOUSEHOLD_CSV_PATH`
  - `SURVEYCTO_BUSINESS_CSV_PATH`
- Runs:
  - `STATA_HOUSEHOLD_MASTER_DO_PATH`
  - `STATA_BUSINESS_MASTER_DO_PATH`
- Appends run logs to `REMOTE_JOBS_LOG_PATH`.

## 6) Scheduled automations

- Morning briefing: 06:30 local timezone
- Evening summary: 19:00 local timezone
- Nightly progress exceptions: `PROGRESS_EXCEPTIONS_HOUR:PROGRESS_EXCEPTIONS_MINUTE`
- Form version monitor: 00:30 local timezone

## 7) Data source rules

- Case dataset (`cases_icm`) uses SurveyCTO API dataset CSV endpoint.
- Form data downloads (HH and Business) use Stata `sctoapi` in automation.
- Form version values shown by bot come from each form Google Sheet `settings` tab, `version` column.

## 8) Quick troubleshooting

Check Python env command path:

- `.\.venv\Scripts\python.exe --version`

Check loaded `sctoapi` date value:

- `.\.venv\Scripts\python.exe -c "from src.config import settings; print(settings.surveycto_sctoapi_date)"`

Check latest automation run logs:

- `Get-Content .cache/remote_jobs_log.jsonl -Tail 5`

Re-run tests for automation service only:

- `.\.venv\Scripts\python.exe -m pytest tests/unit/test_remote_automation_service.py -q`
