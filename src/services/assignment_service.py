"""Assignment-related business logic."""

from src.integrations.google_sheets import GoogleSheetsClient


class AssignmentService:
	"""Provides assignment lookups from sheet data."""

	def __init__(self, sheets_client: GoogleSheetsClient) -> None:
		self.sheets_client = sheets_client

	async def team_assignments(self, team: str) -> list[dict[str, str]]:
		"""Return assignment records for a team."""

		rows = await self.sheets_client.read_assignments()
		return [row for row in rows if row.get("team", "").lower() == team.lower()]

	async def where_is_case(self, case_id: str) -> dict[str, str] | None:
		"""Return assignment row for case, if available."""

		rows = await self.sheets_client.read_assignments()
		for row in rows:
			if row.get("case_id", "").lower() == case_id.lower():
				return row
		return None

	async def team_for_fo(self, fo_name: str) -> str | None:
		"""Return assigned team for given FO."""

		rows = await self.sheets_client.read_assignments()
		for row in rows:
			if row.get("fo", "").lower() == fo_name.lower():
				return row.get("team")
		return None
