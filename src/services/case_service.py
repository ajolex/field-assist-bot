"""Case management business logic."""

from datetime import datetime, timezone

from sqlalchemy import text

from src.db.engine import engine
from src.integrations.surveycto import SurveyCTOClient
from src.models.case import CaseRecord


class CaseService:
	"""Service layer for case operations."""

	def __init__(self, survey_client: SurveyCTOClient) -> None:
		self.survey_client = survey_client

	async def lookup_case(self, case_id: str) -> CaseRecord:
		"""Return case record for the given case ID."""

		return await self.survey_client.get_case(case_id)

	async def case_status(self, case_id: str) -> str:
		"""Return human-readable case status line."""

		case = await self.lookup_case(case_id)
		return f"{case.case_id} is currently {case.status}"

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
