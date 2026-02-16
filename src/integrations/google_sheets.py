"""Google Sheets integration layer."""

from collections.abc import Sequence


class GoogleSheetsClient:
	"""Async wrapper for assignment and productivity data."""

	async def read_assignments(self) -> list[dict[str, str]]:
		"""Return assignment rows.

		This MVP implementation returns static sample rows; replace with gspread-backed
		implementation in production.
		"""

		return [
			{
				"case_id": "H019412021",
				"team": "team_a",
				"fo": "FO-1",
				"barangay": "Bula",
				"municipality": "Mambusao",
				"province": "Capiz",
			}
		]

	async def read_productivity(self) -> list[dict[str, str]]:
		"""Return productivity rows."""

		return [
			{"fo": "FO-1", "team": "team_a", "completed": "4", "target": "3.5"},
			{"fo": "FO-2", "team": "team_a", "completed": "3", "target": "3.5"},
			{"fo": "FO-3", "team": "team_b", "completed": "5", "target": "3.5"},
		]

	async def write_log(self, values: Sequence[str]) -> None:
		"""Write log event (no-op placeholder)."""

		_ = values
