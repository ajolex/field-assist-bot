"""Google Sheets integration layer."""

import asyncio
import base64
import json
from collections.abc import Sequence

import gspread
from google.oauth2.service_account import Credentials

from src.config import settings
from src.utils.logger import get_logger


log = get_logger("google_sheets")


class GoogleSheetsClient:
	"""Async wrapper for assignment and productivity data."""

	def __init__(self) -> None:
		self.has_credentials = bool(settings.google_service_account_json)
		if self.has_credentials:
			try:
				# Decode base64-encoded service account JSON
				creds_json = base64.b64decode(settings.google_service_account_json).decode("utf-8")
				creds_dict = json.loads(creds_json)
				credentials = Credentials.from_service_account_info(
					creds_dict,
					scopes=[
						"https://www.googleapis.com/auth/spreadsheets",
						"https://www.googleapis.com/auth/drive.readonly",
					],
				)
				self.client = gspread.authorize(credentials)
				log.info("google_sheets.initialized", has_credentials=True)
			except Exception as e:
				log.error("google_sheets.init_failed", error=str(e))
				self.has_credentials = False
		else:
			log.warning(
				"google_sheets.no_credentials", message="Using hardcoded sample data"
			)

	async def read_assignments(self) -> list[dict[str, str]]:
		"""Return assignment rows.

		Expected columns: A=date, B=team, C=brgy_prefix, D=(spacer), E-H=stata command
		"""

		if not self.has_credentials:
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

		def _read() -> list[dict[str, str]]:
			try:
				sheet = self.client.open_by_key(settings.google_assignments_sheet_id)
				worksheet = sheet.get_worksheet(0)
				records = worksheet.get_all_records()
				return [dict(record) for record in records]
			except Exception as e:
				log.error("google_sheets.read_assignments_failed", error=str(e))
				return []

		return await asyncio.to_thread(_read)

	async def read_productivity(self) -> list[dict[str, str]]:
		"""Return productivity rows."""

		if not self.has_credentials:
			return [
				{"fo": "FO-1", "team": "team_a", "completed": "4", "target": "3.5"},
				{"fo": "FO-2", "team": "team_a", "completed": "3", "target": "3.5"},
				{"fo": "FO-3", "team": "team_b", "completed": "5", "target": "3.5"},
			]

		def _read() -> list[dict[str, str]]:
			try:
				sheet = self.client.open_by_key(settings.google_productivity_sheet_id)
				worksheet = sheet.get_worksheet(0)
				records = worksheet.get_all_records()
				return [dict(record) for record in records]
			except Exception as e:
				log.error("google_sheets.read_productivity_failed", error=str(e))
				return []

		return await asyncio.to_thread(_read)

	async def write_log(self, values: Sequence[str]) -> None:
		"""Write log event (no-op placeholder)."""

		_ = values

	async def read_form_sheet_tabs(self, sheet_id: str) -> dict[str, list[dict[str, str]]]:
		"""Read all worksheets from a SurveyCTO form Google Sheet."""

		if not self.has_credentials or not sheet_id.strip():
			return {}

		def _read() -> dict[str, list[dict[str, str]]]:
			try:
				sheet = self.client.open_by_key(sheet_id)
				result: dict[str, list[dict[str, str]]] = {}
				for worksheet in sheet.worksheets():
					try:
						records = worksheet.get_all_records()
					except Exception:
						records = []
					result[worksheet.title] = [dict(record) for record in records]
				return result
			except Exception as e:
				log.error("google_sheets.read_form_sheet_tabs_failed", sheet_id=sheet_id, error=str(e))
				return {}

		return await asyncio.to_thread(_read)

	async def surveycto_issue_context(
		self,
		issue_text: str,
		variable_hints: list[str],
		max_rows: int = 20,
	) -> str:
		"""Build compact context from configured form sheets for issue troubleshooting."""

		if not self.has_credentials:
			return ""

		keywords = {word.lower() for word in issue_text.split() if len(word) >= 3}
		keywords.update(hint.lower() for hint in variable_hints)
		if not keywords:
			return ""

		sections: list[str] = []
		for form_name, sheet_id in settings.surveycto_form_sheet_ids.items():
			tabs = await self.read_form_sheet_tabs(sheet_id)
			if not tabs:
				continue

			matches: list[str] = []
			for tab_name, rows in tabs.items():
				for row in rows:
					name = str(row.get("name", "")).strip()
					type_ = str(row.get("type", "")).strip()
					relevant = str(row.get("relevant", "")).strip()
					constraint = str(row.get("constraint", "")).strip()
					label = ""
					for key, value in row.items():
						if str(key).lower().startswith("label") and str(value).strip():
							label = str(value).strip()
							break

					combined = f"{name} {type_} {label} {relevant} {constraint}".lower()
					if not combined.strip():
						continue

					if any(keyword in combined for keyword in keywords):
						matches.append(
							f"[{tab_name}] name={name or '-'} type={type_ or '-'} "
							f"relevant={relevant or '-'} constraint={constraint or '-'} label={label or '-'}"
						)
						if len(matches) >= max_rows:
							break
				if len(matches) >= max_rows:
					break

			if matches:
				sections.append(f"Form {form_name}:\n" + "\n".join(matches))

		return "\n\n".join(sections)
