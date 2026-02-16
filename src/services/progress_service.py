"""Progress and productivity business logic."""

from src.integrations.google_sheets import GoogleSheetsClient


class ProgressService:
	"""Service for progress summaries."""

	def __init__(self, sheets_client: GoogleSheetsClient) -> None:
		self.sheets_client = sheets_client

	async def completion_rate(self, completed: int, total: int) -> float:
		"""Compute completion percentage with zero-safe handling."""

		if total <= 0:
			return 0.0
		return (completed / total) * 100.0

	async def overall_progress(self) -> dict[str, float]:
		"""Compute overall completion metrics from sheet data."""

		rows = await self.sheets_client.read_productivity()
		completed_values = [float(row.get("completed", "0")) for row in rows]
		target_values = [float(row.get("target", "0")) for row in rows]
		completed_total = sum(completed_values)
		target_total = sum(target_values)
		return {
			"completed": completed_total,
			"target": target_total,
			"rate": await self.completion_rate(int(completed_total), int(target_total) or 1),
		}

	async def team_status(self, team_name: str) -> dict[str, float]:
		"""Return team-specific progress metrics."""

		rows = await self.sheets_client.read_productivity()
		filtered = [row for row in rows if row.get("team", "").lower() == team_name.lower()]
		completed = sum(float(row.get("completed", "0")) for row in filtered)
		target = sum(float(row.get("target", "0")) for row in filtered)
		rate = await self.completion_rate(int(completed), int(target) or 1)
		return {"completed": completed, "target": target, "rate": rate}

	async def fo_productivity(self, fo_name: str) -> dict[str, float]:
		"""Return individual productivity metrics."""

		rows = await self.sheets_client.read_productivity()
		for row in rows:
			if row.get("fo", "").lower() == fo_name.lower():
				completed = float(row.get("completed", "0"))
				target = float(row.get("target", "0"))
				return {
					"completed": completed,
					"target": target,
					"rate": await self.completion_rate(int(completed), int(target) or 1),
				}
		return {"completed": 0.0, "target": 0.0, "rate": 0.0}
