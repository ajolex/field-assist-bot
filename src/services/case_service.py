"""Case management business logic."""

import re
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import text

from src.config import settings
from src.db.engine import engine
from src.integrations.surveycto import SurveyCTOClient
from src.models.case import CaseRecord
from src.services.escalation_service import EscalationService
from src.utils.logger import get_logger


_TEAM_PATTERN = re.compile(r"\bteam_[a-f]\b", re.IGNORECASE)
log = get_logger("case_service")


def _wants_status_change(text: str) -> bool:
	lower = text.lower()
	keywords = (
		"reopen",
		"re-open",
		"open again",
		"reassign",
		"re-assign",
		"change status",
		"move to team",
	)
	return any(keyword in lower for keyword in keywords)


class CaseService:
	"""Service layer for case operations."""

	def __init__(
		self,
		survey_client: SurveyCTOClient,
		escalation_service: EscalationService | None = None,
	) -> None:
		self.survey_client = survey_client
		self.escalation_service = escalation_service

	async def lookup_case(self, case_id: str) -> CaseRecord:
		"""Return case record for the given case ID."""

		return await self.survey_client.get_case(case_id)

	async def case_status(
		self,
		case_id: str,
		requester: str | None = None,
		channel: str = "#case-status",
		request_text: str = "",
	) -> str:
		"""Return human-readable case status line."""
		resolved: tuple[str, str] | None = None
		try:
			resolved = await self._resolve_status_from_cases_csv(case_id)
		except Exception as error:
			log.warning(
				"case_status.csv_lookup_failed",
				case_id=case_id,
				error=str(error),
			)

		if resolved is not None:
			status_text, details = resolved
			response = f"{case_id} status: {status_text}. {details}".strip()
			if (
				request_text
				and _wants_status_change(request_text)
				and self.escalation_service is not None
				and requester is not None
			):
				escalation_id = await self.escalation_service.create_escalation(
					requester=requester,
					reason=f"Case status change request for {case_id}",
					channel=channel,
					case_id=case_id,
					question=request_text,
				)
				response += (
					f"\n\n🔔 I escalated this change request for review "
					f"(Escalation ID: **{escalation_id}**)."
				)
			return response

		case = await self.lookup_case(case_id)
		return f"{case.case_id} is currently {case.status}"

	async def _resolve_status_from_cases_csv(self, case_id: str) -> tuple[str, str] | None:
		rows = await self.survey_client.fetch_cases_rows_with_fallback(
			settings.surveycto_cases_source_id,
			output_path=Path(settings.surveycto_cases_csv_path),
		)
		if not rows:
			return None

		needle = case_id.strip().lower()
		matched_row: dict[str, str] | None = None
		for row in rows:
			row_case_id = str(row.get("caseid", row.get("id", ""))).strip().lower()
			if row_case_id == needle:
				matched_row = row
				break
		if matched_row is None:
			return "not found", "Case ID not found in cases form export."

		users_value = str(matched_row.get("users", "")).strip()
		normalized_users = users_value.lower()

		if "closed" in normalized_users:
			return "closed", "Marked completed in `users` column."
		if "refused" in normalized_users:
			return "refused", "Marked refusal in `users` column."

		team_match = _TEAM_PATTERN.search(normalized_users)
		if team_match:
			team_name = team_match.group(0)
			return "open", f"Currently assigned to **{team_name}**."

		if normalized_users:
			return "open", f"Current assignee marker in `users`: `{users_value}`."
		return "open", "No assignee marker in `users`; likely unassigned/open."

	async def team_cases(self, team_name: str) -> list[CaseRecord]:
		"""Return open cases for a team."""

		sample_ids = ["H019412021", "H030832011"]
		results: list[CaseRecord] = []
		for case_id in sample_ids:
			case = await self.lookup_case(case_id)
			if case.team and case.team.lower() == team_name.lower() and case.status.lower() == "open":
				results.append(case)
		return results

	async def request_reopen(self, case_id: str, requester: str, reason: str) -> None:
		"""Store reopen request for review."""

		payload = {
			"case_id": case_id,
			"requester": requester,
			"reason": reason,
			"status": "open",
			"created_at": datetime.now(timezone.utc).isoformat(),
		}
		async with engine.begin() as conn:
			await conn.execute(
				text(
					"""
					INSERT INTO reopen_requests (case_id, requester, reason, status, created_at)
					VALUES (:case_id, :requester, :reason, :status, :created_at)
					"""
				),
				payload,
			)

	@staticmethod
	def redact_pii(case: CaseRecord) -> CaseRecord:
		"""Return redacted case record safe for Discord output."""

		return CaseRecord(
			case_id=case.case_id,
			status=case.status,
			team=case.team,
			barangay=case.barangay,
			municipality=case.municipality,
			province=case.province,
			forms=case.forms,
			treatment=case.treatment,
			updated_at=case.updated_at,
		)
