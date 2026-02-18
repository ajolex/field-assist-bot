"""Intent classification for natural language bot mentions."""

import re
from enum import Enum

from src.integrations.openai_client import OpenAIClient
from src.utils.logger import get_logger

log = get_logger("intent_classifier")


class Intent(str, Enum):
    """Classified user intents."""

    PROTOCOL = "protocol"
    CASE_LOOKUP = "case_lookup"
    CASE_STATUS = "case_status"
    ASSIGNMENTS = "assignments"
    PROGRESS = "progress"
    FORM_VERSION = "form_version"
    SURVEYCTO_ISSUE = "surveycto_issue"
    ESCALATION = "escalation"
    GREETING = "greeting"
    # Remote control intents (private channel only)
    RC_SYS_STATUS = "rc_sys_status"
    RC_PROCESSES = "rc_processes"
    RC_KILL = "rc_kill"
    RC_FILE_FIND = "rc_file_find"
    RC_FILE_SEND = "rc_file_send"
    RC_FILE_SAVE = "rc_file_save"
    RC_FILE_SIZE = "rc_file_size"
    RC_FILE_ZIP = "rc_file_zip"
    RC_SCREENSHOT = "rc_screenshot"
    RC_APP_OPEN = "rc_app_open"
    RC_APP_CLOSE = "rc_app_close"
    RC_APP_RUN = "rc_app_run"
    RC_WEB_DOWNLOAD = "rc_web_download"
    RC_WEB_PING = "rc_web_ping"
    RC_GIT_STATUS = "rc_git_status"
    RC_GIT_PULL = "rc_git_pull"
    # Automation job intents
    RC_DOWNLOAD_HH = "rc_download_hh"
    RC_DOWNLOAD_BIZ = "rc_download_biz"
    RC_DOWNLOAD_PHASE_A = "rc_download_phase_a"
    RC_RUN_HH_DMS = "rc_run_hh_dms"
    RC_RUN_BIZ_DMS = "rc_run_biz_dms"
    RC_RUN_DMS = "rc_run_dms"
    UNKNOWN = "unknown"


# Quick regex patterns for high-confidence shortcuts (skip LLM call)
_CASE_ID_PATTERN = re.compile(
    r"\b(?:case|check|status|look\s?up|find)\b.*\b([A-Z0-9]{4,}[-_]?\d+)\b",
    re.IGNORECASE,
)
_GREETING_PATTERN = re.compile(
    r"^(hi|hello|hey|good\s*(morning|afternoon|evening)|sup|yo)\b",
    re.IGNORECASE,
)
_SURVEY_ISSUE_PATTERN = re.compile(
    r"\b(surveycto|xlsform|skip\s*logic|relevance|constraint|calculation|question\s*name|variable)\b",
    re.IGNORECASE,
)
_CASE_STATUS_PATTERN = re.compile(
    (
        r"\b("
        r"status|open|opened|close|closed|check|checked|verify|verified|"
        r"refused|reopen|re-open|reassign|re-assign|assigned"
        r")\b"
    ),
    re.IGNORECASE,
)

# Remote-control fast-path patterns
_RC_SCREENSHOT_PATTERN = re.compile(
    r"\b(screenshot|screen\s*shot|screen\s*cap(ture)?|take.*screen|show.*screen)\b",
    re.IGNORECASE,
)
_RC_SYS_STATUS_PATTERN = re.compile(
    r"\b(cpu|ram|memory|disk|uptime|system\s*status|pc\s*status|computer\s*status|how.*my.*(?:pc|computer|machine))\b",
    re.IGNORECASE,
)
_RC_PROCESSES_PATTERN = re.compile(
    r"\b(processes|task\s*manager|what.*running|running\s*processes|top\s*processes)\b",
    re.IGNORECASE,
)
_RC_GIT_PATTERN = re.compile(
    r"\b(git\s+(pull|status|st))\b",
    re.IGNORECASE,
)
_RC_DMS_PATTERN = re.compile(
    r"\b(run\s+(the\s+)?dms|run\s+(the\s+)?(full|daily)\s*(pipeline|job|automation)|scto_dms_daily)\b",
    re.IGNORECASE,
)
_RC_DOWNLOAD_FORM_PATTERN = re.compile(
    r"\b(download|pull|fetch|get)\b.*(household|hh|business|biz|phase\s*a|revisit)\b.*(csv|data|form|survey)?\b",
    re.IGNORECASE,
)
_RC_RUN_STATA_PATTERN = re.compile(
    r"\b(run|execute)\b.*(household|hh|business|biz)\b.*(dms|stata|do\s*file|master)\b",
    re.IGNORECASE,
)

CLASSIFICATION_PROMPT = """You are an intent classifier for a field research operations Discord bot.
The bot also has remote PC control capabilities.

Classify the user's message into EXACTLY ONE of these intents:
- PROTOCOL: Questions about study protocol, survey procedures, questionnaire guidance, field scenarios, how to handle situations, ICM rules, data collection rules, respondent eligibility, PSPS, SurveyCTO troubleshooting
- CASE_LOOKUP: Requests to look up or check a specific case by ID (e.g. "check case ABC-123")
- CASE_STATUS: Asking about case status without a specific ID, or asking about team cases
- ASSIGNMENTS: Questions about who is assigned where, team assignments, field officer locations
- PROGRESS: Questions about progress, productivity, completion rates, targets, team performance
- FORM_VERSION: Questions about form versions, form updates, changelogs
- SURVEYCTO_ISSUE: Reports of form behavior bugs, skip logic problems, relevance/constraint issues, question appearing unexpectedly
- ESCALATION: Explicit requests to escalate something to a supervisor, or reporting issues/incidents
- GREETING: Simple greetings with no real question
- RC_SYS_STATUS: Asking about PC health, CPU, RAM, disk, uptime, system status
- RC_PROCESSES: Asking what processes are running, show task manager, top processes
- RC_KILL: Kill or end a process by name
- RC_FILE_FIND: Search for files by name/pattern on the PC
- RC_FILE_SEND: Send/upload/get a specific file from the PC
- RC_FILE_SAVE: Save or download something TO the PC (from Discord or a URL)
- RC_FILE_SIZE: Check the size of a file or folder
- RC_FILE_ZIP: Zip a file/folder and send it
- RC_SCREENSHOT: Take a screenshot of the PC screen (optionally of a specific window/app)
- RC_APP_OPEN: Open/launch a file or application
- RC_APP_CLOSE: Close/quit an application
- RC_APP_RUN: Run a PowerShell script (.ps1)
- RC_WEB_DOWNLOAD: Download a URL to a folder on the PC
- RC_WEB_PING: Check if a website/URL is reachable
- RC_GIT_STATUS: Check git status of a repository
- RC_GIT_PULL: Pull latest changes in a git repository
- RC_DOWNLOAD_HH: Download only the household survey form CSV from SurveyCTO (no Stata)
- RC_DOWNLOAD_BIZ: Download only the ICM business module CSV from SurveyCTO (no Stata)
- RC_DOWNLOAD_PHASE_A: Download the Phase A revisit form CSV from SurveyCTO (no Stata)
- RC_RUN_HH_DMS: Run only the household Stata DMS (do-file) without downloading
- RC_RUN_BIZ_DMS: Run only the business Stata DMS (do-file) without downloading
- RC_RUN_DMS: Run full daily pipeline — download all SurveyCTO CSVs and run all Stata DMS
- UNKNOWN: Cannot classify

Respond with ONLY the intent name (e.g. PROTOCOL). Nothing else."""


class IntentClassifier:
    """Classifies user messages into actionable intents."""

    def __init__(self, openai_client: OpenAIClient) -> None:
        self.openai_client = openai_client

    async def classify(self, message: str) -> tuple[Intent, str | None]:
        """Classify a message and optionally extract a parameter (e.g. case ID).

        Returns (intent, extracted_param).
        """

        text = message.strip()

        # Fast-path: greeting
        if _GREETING_PATTERN.match(text):
            return Intent.GREETING, None

        # Fast-path: explicit case ID mentioned
        case_match = _CASE_ID_PATTERN.search(text)
        if case_match:
            case_id = case_match.group(1)
            if _CASE_STATUS_PATTERN.search(text):
                return Intent.CASE_STATUS, case_id
            return Intent.CASE_LOOKUP, case_id

        # Fast-path: remote control — screenshot (pass text for window name)
        if _RC_SCREENSHOT_PATTERN.search(text):
            return Intent.RC_SCREENSHOT, text

        # Fast-path: remote control — system status
        if _RC_SYS_STATUS_PATTERN.search(text):
            return Intent.RC_SYS_STATUS, None

        # Fast-path: remote control — processes
        if _RC_PROCESSES_PATTERN.search(text):
            return Intent.RC_PROCESSES, None

        # Fast-path: remote control — git
        if _RC_GIT_PATTERN.search(text):
            if re.search(r"\bgit\s+pull\b", text, re.IGNORECASE):
                return Intent.RC_GIT_PULL, text
            return Intent.RC_GIT_STATUS, text

        # Fast-path: automation jobs — run full DMS pipeline
        if _RC_DMS_PATTERN.search(text):
            return Intent.RC_RUN_DMS, None

        # Fast-path: run individual Stata DMS
        if _RC_RUN_STATA_PATTERN.search(text):
            if re.search(r"\b(household|hh)\b", text, re.IGNORECASE):
                return Intent.RC_RUN_HH_DMS, None
            return Intent.RC_RUN_BIZ_DMS, None

        # Fast-path: download individual SurveyCTO form
        if _RC_DOWNLOAD_FORM_PATTERN.search(text):
            if re.search(r"\b(phase\s*a|revisit)\b", text, re.IGNORECASE):
                return Intent.RC_DOWNLOAD_PHASE_A, None
            if re.search(r"\b(business|biz)\b", text, re.IGNORECASE):
                return Intent.RC_DOWNLOAD_BIZ, None
            return Intent.RC_DOWNLOAD_HH, None

        # Fast-path: SurveyCTO form issue phrasing
        if _SURVEY_ISSUE_PATTERN.search(text):
            return Intent.SURVEYCTO_ISSUE, None

        # Use LLM for everything else
        if not self.openai_client.has_api_key:
            return Intent.PROTOCOL, None

        try:
            response = await self.openai_client.chat_with_system_prompt(
                system_prompt=CLASSIFICATION_PROMPT,
                user_message=text,
                context="",
            )
            intent_str = response.strip().upper().replace(" ", "_")

            # Extract case ID if classified as case-related
            extracted = None
            case_id_match = re.search(r"\b([A-Z0-9]{3,}[-_]?\d+)\b", text, re.IGNORECASE)
            if case_id_match and intent_str in ("CASE_LOOKUP", "CASE_STATUS"):
                extracted = case_id_match.group(1)

            # For remote control intents, pass raw text for parameter extraction
            if intent_str.startswith("RC_"):
                extracted = text

            try:
                intent = Intent(intent_str.lower())
            except ValueError:
                log.warning("intent.unknown_classification", raw=intent_str)
                intent = Intent.PROTOCOL  # Default to protocol for field questions

            return intent, extracted

        except Exception as e:
            log.error("intent.classification_failed", error=str(e))
            return Intent.PROTOCOL, None
