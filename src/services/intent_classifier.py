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

CLASSIFICATION_PROMPT = """You are an intent classifier for a field research operations Discord bot.

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
- UNKNOWN: Cannot classify or not related to field operations

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

            try:
                intent = Intent(intent_str.lower())
            except ValueError:
                log.warning("intent.unknown_classification", raw=intent_str)
                intent = Intent.PROTOCOL  # Default to protocol for field questions

            return intent, extracted

        except Exception as e:
            log.error("intent.classification_failed", error=str(e))
            return Intent.PROTOCOL, None
