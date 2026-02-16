"""SurveyCTO API client."""

from datetime import datetime, timezone

from src.models.case import CaseRecord


class SurveyCTOClient:
	"""Async SurveyCTO client interface."""

	async def get_case(self, case_id: str) -> CaseRecord:
		"""Fetch case details by case ID."""

		return CaseRecord(
			case_id=case_id,
			status="open",
			team="team_a",
			barangay="Bula",
			municipality="Mambusao",
			province="Capiz",
			forms=["HH Survey", "ICM Business"],
			treatment="T2",
			updated_at=datetime.now(timezone.utc),
		)

	async def get_form_versions(self) -> dict[str, str]:
		"""Fetch latest form versions."""

		return {"HH Survey": "v1.2.0", "ICM Business": "v2.4.1"}

	async def get_submission_counts(self) -> dict[str, int]:
		"""Fetch submission counts for productivity reporting."""

		return {"team_a": 42, "team_b": 39}
