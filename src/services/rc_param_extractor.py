"""Extract structured parameters from natural language remote-control requests.

Uses a lightweight LLM call to pull file paths, process names, URLs, repo paths,
etc. from freeform text so the remote_control_service functions get clean inputs.
"""

from __future__ import annotations

import json

from src.integrations.openai_client import OpenAIClient
from src.utils.logger import get_logger

log = get_logger("rc_param_extractor")

_EXTRACTION_PROMPT = """\
Extract parameters from the user's remote-control request.
Return ONLY a JSON object with the relevant keys below (omit keys that don't apply):

- "path": a file or folder path on the PC
- "pattern": a filename search pattern (e.g. *.xlsx, report*)
- "search_root": folder to search in (only if the user specifies one)
- "name": process or application name
- "url": a URL
- "dest_folder": destination folder for saving/downloading
- "repo_path": path to a git repository
- "top_n": number of items to show (integer)
- "window_name": the name of a specific window or app to screenshot

Rules:
- Paths use Windows backslash format unless the user used forward slashes
- If the user says "my desktop" use C:\\Users\\AJolex\\Desktop
- If the user says "my documents" use C:\\Users\\AJolex\\Documents
- If the user says "my downloads" use C:\\Users\\AJolex\\Downloads
- If the user says "this repo" or "this project" use G:\\field-assist-bot
- For app names: "Teams" = "ms-teams", "Chrome" = "chrome", "Stata" = "stata", \
"Excel" = "excel", "Word" = "winword", "VS Code"/"Code" = "code", \
"Notepad" = "notepad", "Outlook" = "outlook", "Slack" = "slack"
- For screenshot of a specific app, extract the app name into "window_name"
- If no specific value is given for a key, omit it
- Return valid JSON only, no explanation"""


async def extract_params(
    openai_client: OpenAIClient,
    intent: str,
    raw_text: str,
) -> dict[str, str]:
    """Use LLM to extract structured params from natural language.

    Returns a dict of param_name -> value.  Empty dict on failure.
    """
    if not openai_client.has_api_key or not raw_text.strip():
        return {}

    try:
        response = await openai_client.chat_with_system_prompt(
            system_prompt=_EXTRACTION_PROMPT,
            user_message=f"Intent: {intent}\nRequest: {raw_text}",
            context="",
        )
        # Strip markdown fences if the model wraps in ```json
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            return {str(k): str(v) for k, v in parsed.items()}
        return {}
    except (json.JSONDecodeError, Exception) as e:
        log.warning("rc_param_extractor.failed", error=str(e), raw=raw_text[:120])
        return {}
