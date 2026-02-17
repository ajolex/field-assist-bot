"""Discord-native field issue triage service."""

import asyncio
import json
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from src.config import settings
from src.integrations.openai_client import OpenAIClient
from src.utils.logger import get_logger

log = get_logger("issue_triage")


@dataclass
class FieldIssueRecord:
	"""Structured field issue payload persisted to disk."""

	issue_id: str
	reported_at: str
	reporter_id: str
	source_channel_id: str
	source_message_id: str
	form_name: str
	variable_name: str
	case_id: str
	severity: str
	device_info: str
	workaround: str
	owner: str
	status: str
	description: str
	thread_channel_id: str = ""
	summary_message_id: str = ""
	screenshot_urls: list[str] | None = None


class IssueTriageService:
	"""Build, persist, and update structured field issues."""

	def __init__(self, openai_client: OpenAIClient) -> None:
		"""Initialize with OpenAI-backed extraction support."""
		self.openai_client = openai_client
		self.records_path = Path(settings.issue_records_path)
		self.status_log_path = Path(settings.issue_status_log_path)

	@staticmethod
	def _detect_form_name(text: str) -> str:
		lower = text.lower()
		if "business" in lower or "icm business" in lower:
			return "ICM Business"
		if "household" in lower or "hh" in lower:
			return "ICM Household"
		if "phase a" in lower or "revisit" in lower:
			return "Phase A Revisit"
		return "Unknown"

	@staticmethod
	def _detect_severity(text: str) -> str:
		lower = text.lower()
		if any(token in lower for token in ["cannot submit", "blocked", "crash", "critical"]):
			return "high"
		if any(token in lower for token in ["wrong", "invalid", "error", "missing"]):
			return "medium"
		return "low"

	@staticmethod
	def _extract_variable(text: str) -> str:
		matches = re.findall(r"\b[a-zA-Z][a-zA-Z0-9_]{2,}\b", text)
		for token in matches:
			if "_" in token or token.lower().startswith(("q", "hh", "icm", "s")):
				return token
		return "unknown"

	@staticmethod
	def _extract_case_id(text: str) -> str:
		match = re.search(r"\b[A-Za-z]\d{8,}\b", text)
		if match:
			return match.group(0)
		return "unknown"

	async def _extract_with_llm(self, description: str) -> dict[str, str]:
		system_prompt = (
			"Extract a structured SurveyCTO field issue report. "
			"Return strict JSON with keys: form_name, variable_name, case_id, "
			"severity, device_info, workaround. "
			"Severity must be one of low, medium, high. If unknown use 'unknown'."
		)
		answer = await self.openai_client.chat_with_system_prompt(
			system_prompt=system_prompt,
			user_message=description,
			context="No external context required.",
		)
		try:
			payload = json.loads(answer)
			if isinstance(payload, dict):
				return {str(k): str(v) for k, v in payload.items()}
		except json.JSONDecodeError:
			log.warning("issue_triage.llm_json_parse_failed")
		return {}

	async def create_issue(
		self,
		*,
		reporter_id: str,
		source_channel_id: str,
		source_message_id: str,
		description: str,
		screenshot_urls: list[str],
		device_info_hint: str = "",
		owner_hint: str = "",
	) -> FieldIssueRecord:
		"""Create and persist a new issue record."""
		llm_data = await self._extract_with_llm(description)
		now = datetime.now(UTC).isoformat()
		issue_id = f"FI-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}-{uuid4().hex[:6]}"
		form_name = llm_data.get("form_name") or self._detect_form_name(description)
		variable_name = llm_data.get("variable_name") or self._extract_variable(description)
		case_id = llm_data.get("case_id") or self._extract_case_id(description)
		severity = (llm_data.get("severity") or self._detect_severity(description)).lower()
		if severity not in {"low", "medium", "high"}:
			severity = "medium"
		device_info = llm_data.get("device_info") or device_info_hint or "unknown"
		workaround = (
			llm_data.get("workaround")
			or "Capture screenshot and continue with comment if possible."
		)
		owner = owner_hint or settings.default_issue_owner

		record = FieldIssueRecord(
			issue_id=issue_id,
			reported_at=now,
			reporter_id=reporter_id,
			source_channel_id=source_channel_id,
			source_message_id=source_message_id,
			form_name=form_name,
			variable_name=variable_name,
			case_id=case_id,
			severity=severity,
			device_info=device_info,
			workaround=workaround,
			owner=owner,
			status="open",
			description=description.strip(),
			screenshot_urls=screenshot_urls,
		)
		await self._upsert_record(record)
		await self._append_status_log(
			issue_id=issue_id,
			status="open",
			actor=reporter_id,
			note="Issue created",
			owner=owner,
		)
		return record

	async def attach_thread(
		self,
		issue_id: str,
		thread_channel_id: str,
		summary_message_id: str,
	) -> None:
		"""Persist thread/message linkage for an issue."""
		record = await self.get_issue(issue_id)
		if record is None:
			return
		record.thread_channel_id = thread_channel_id
		record.summary_message_id = summary_message_id
		await self._upsert_record(record)

	async def update_status(
		self,
		*,
		issue_id: str,
		status: str,
		actor: str,
		note: str,
		owner: str | None = None,
	) -> FieldIssueRecord | None:
		"""Update issue status and append lightweight history log."""
		record = await self.get_issue(issue_id)
		if record is None:
			return None
		record.status = status
		if owner:
			record.owner = owner
		await self._upsert_record(record)
		await self._append_status_log(
			issue_id=issue_id,
			status=status,
			actor=actor,
			note=note,
			owner=record.owner,
		)
		return record

	async def get_issue(self, issue_id: str) -> FieldIssueRecord | None:
		"""Load issue by ID from the local JSON store."""
		records = await self._load_records()
		payload = records.get(issue_id)
		if payload is None:
			return None
		raw_screenshot_urls = payload.get("screenshot_urls", [])
		screenshot_urls = raw_screenshot_urls if isinstance(raw_screenshot_urls, list) else []
		issue_payload = {
			"issue_id": str(payload.get("issue_id", "")),
			"reported_at": str(payload.get("reported_at", "")),
			"reporter_id": str(payload.get("reporter_id", "")),
			"source_channel_id": str(payload.get("source_channel_id", "")),
			"source_message_id": str(payload.get("source_message_id", "")),
			"form_name": str(payload.get("form_name", "Unknown")),
			"variable_name": str(payload.get("variable_name", "unknown")),
			"case_id": str(payload.get("case_id", "unknown")),
			"severity": str(payload.get("severity", "medium")),
			"device_info": str(payload.get("device_info", "unknown")),
			"workaround": str(payload.get("workaround", "")),
			"owner": str(payload.get("owner", settings.default_issue_owner)),
			"status": str(payload.get("status", "open")),
			"description": str(payload.get("description", "")),
			"thread_channel_id": str(payload.get("thread_channel_id", "")),
			"summary_message_id": str(payload.get("summary_message_id", "")),
			"screenshot_urls": [
				str(url)
				for url in screenshot_urls
				if isinstance(url, str)
			],
		}
		return FieldIssueRecord(**issue_payload)

	async def get_status_history(self, issue_id: str, limit: int = 20) -> list[dict[str, str]]:
		"""Return latest status log events for an issue."""
		if not self.status_log_path.exists():
			return []

		def _read() -> list[dict[str, str]]:
			rows: list[dict[str, str]] = []
			for line in self.status_log_path.read_text(encoding="utf-8").splitlines():
				line = line.strip()
				if not line:
					continue
				try:
					item = json.loads(line)
				except json.JSONDecodeError:
					continue
				if str(item.get("issue_id", "")) == issue_id:
					rows.append({str(k): str(v) for k, v in item.items()})
			return rows[-limit:]

		return await asyncio.to_thread(_read)

	def render_summary(self, issue: FieldIssueRecord) -> str:
		"""Render issue card for thread pinning."""
		screenshot_block = (
			"\n".join(f"- {url}" for url in (issue.screenshot_urls or [])) or "- none"
		)
		return (
			f"🧾 **Field Issue {issue.issue_id}**\n"
			f"- **Status:** {issue.status}\n"
			f"- **Severity:** {issue.severity}\n"
			f"- **Owner:** {issue.owner}\n"
			f"- **Form:** {issue.form_name}\n"
			f"- **Variable:** {issue.variable_name}\n"
			f"- **Case ID:** {issue.case_id}\n"
			f"- **FO Device:** {issue.device_info}\n"
			f"- **Workaround:** {issue.workaround}\n"
			f"- **Description:** {issue.description[:500]}\n"
			f"- **Screenshots:**\n{screenshot_block}"
		)

	async def _append_status_log(
		self,
		*,
		issue_id: str,
		status: str,
		actor: str,
		note: str,
		owner: str,
	) -> None:
		self.status_log_path.parent.mkdir(parents=True, exist_ok=True)
		event = {
			"issue_id": issue_id,
			"timestamp": datetime.now(UTC).isoformat(),
			"status": status,
			"actor": actor,
			"owner": owner,
			"note": note,
		}

		def _write() -> None:
			with self.status_log_path.open("a", encoding="utf-8") as handle:
				handle.write(json.dumps(event, ensure_ascii=False) + "\n")

		await asyncio.to_thread(_write)

	async def _upsert_record(self, record: FieldIssueRecord) -> None:
		records = await self._load_records()
		records[record.issue_id] = asdict(record)

		def _write() -> None:
			self.records_path.parent.mkdir(parents=True, exist_ok=True)
			self.records_path.write_text(
				json.dumps(records, ensure_ascii=False, indent=2),
				encoding="utf-8",
			)

		await asyncio.to_thread(_write)

	async def _load_records(self) -> dict[str, dict[str, object]]:
		if not self.records_path.exists():
			return {}

		def _read() -> dict[str, dict[str, object]]:
			try:
				payload = json.loads(self.records_path.read_text(encoding="utf-8"))
			except json.JSONDecodeError:
				return {}
			if isinstance(payload, dict):
				return payload
			return {}

		return await asyncio.to_thread(_read)
