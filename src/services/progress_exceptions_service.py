"""Detect and report productivity exceptions instead of full dashboards."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from src.config import settings
from src.integrations.google_sheets import GoogleSheetsClient


@dataclass
class ProgressExceptionReport:
	"""Structured anomaly report."""

	has_anomalies: bool
	text: str


@dataclass
class ProductivityRow:
	"""Normalized productivity row for exception checks."""

	fo_name: str
	team_name: str
	completed: float
	missing: bool


class ProgressExceptionsService:
	"""Build nightly anomaly-focused productivity alerts."""

	def __init__(self, sheets_client: GoogleSheetsClient) -> None:
		"""Initialize with a Google Sheets data source."""
		self.sheets_client = sheets_client
		self.snapshots_path = Path(settings.progress_snapshots_path)

	async def build_nightly_report(self) -> ProgressExceptionReport:
		"""Compute under-target, missing, and drop anomalies."""
		rows = await self.sheets_client.read_productivity()
		current = self._normalize_rows(rows)
		previous = await self._latest_snapshot()

		under_target: list[str] = []
		missing_reports: list[str] = []
		sudden_drops: list[str] = []
		team_lagging: list[str] = []

		for fo_name, payload in current.items():
			completed = payload.completed
			team = payload.team_name
			if payload.missing:
				missing_reports.append(f"{fo_name} ({team})")
				continue
			if completed < settings.progress_exception_min_target:
				under_target.append(
					f"{fo_name} ({team}) = {completed:.1f} "
					f"(< {settings.progress_exception_min_target:.1f})"
				)
			prev_payload = previous.get(fo_name)
			if prev_payload is not None:
				drop = prev_payload.completed - completed
				if drop >= settings.progress_exception_drop_threshold:
					sudden_drops.append(
						f"{fo_name} ({team}) dropped by {drop:.1f} vs yesterday"
					)

		team_scores: dict[str, list[float]] = {}
		for payload in current.values():
			if payload.missing:
				continue
			team_scores.setdefault(payload.team_name, []).append(payload.completed)
		for team_name, completions in team_scores.items():
			if not completions:
				continue
			average = sum(completions) / len(completions)
			if average < settings.progress_exception_min_target:
				team_lagging.append(
					f"{team_name} team average = {average:.2f} "
					f"(< {settings.progress_exception_min_target:.1f})"
				)

		await self._append_snapshot(current)

		sections: list[str] = []
		if under_target:
			sections.append(
				"**Under-target FOs**\n" + "\n".join(f"- {line}" for line in under_target)
			)
		if team_lagging:
			sections.append(
				"**Teams Falling Behind**\n" + "\n".join(f"- {line}" for line in team_lagging)
			)
		if sudden_drops:
			sections.append(
				"**Sudden Drops vs Yesterday**\n"
				+ "\n".join(f"- {line}" for line in sudden_drops)
			)
		if missing_reports:
			sections.append(
				"**Missing Reports**\n" + "\n".join(f"- {line}" for line in missing_reports)
			)

		if not sections:
			return ProgressExceptionReport(has_anomalies=False, text="")

		mention = (
			f"<@&{settings.field_manager_role_id}>"
			if settings.field_manager_role_id
			else "@FM"
		)
		body = "\n\n".join(sections)
		text = f"⚠️ {mention} Nightly productivity exceptions\n\n{body}"
		return ProgressExceptionReport(has_anomalies=True, text=text)

	@staticmethod
	def _to_float(value: object) -> tuple[float, bool]:
		if value is None:
			return 0.0, True
		cleaned = str(value).strip()
		if not cleaned:
			return 0.0, True
		try:
			return float(cleaned), False
		except ValueError:
			return 0.0, True

	def _normalize_rows(self, rows: list[dict[str, str]]) -> dict[str, ProductivityRow]:
		normalized: dict[str, ProductivityRow] = {}
		for row in rows:
			fo_name = str(row.get("fo", "")).strip() or "unknown_fo"
			team_name = str(row.get("team", "")).strip() or "unknown_team"
			completed, missing = self._to_float(row.get("completed"))
			normalized[fo_name] = ProductivityRow(
				fo_name=fo_name,
				team_name=team_name,
				completed=completed,
				missing=missing,
			)
		return normalized

	async def _append_snapshot(self, snapshot: dict[str, ProductivityRow]) -> None:
		event = {
			"captured_at": datetime.now(UTC).isoformat(),
			"fo": {
				fo_name: {
					"team": payload.team_name,
					"completed": payload.completed,
					"missing": payload.missing,
				}
				for fo_name, payload in snapshot.items()
			},
		}
		self.snapshots_path.parent.mkdir(parents=True, exist_ok=True)

		def _write() -> None:
			with self.snapshots_path.open("a", encoding="utf-8") as handle:
				handle.write(json.dumps(event, ensure_ascii=False) + "\n")

		await asyncio.to_thread(_write)

	async def _latest_snapshot(self) -> dict[str, ProductivityRow]:
		if not self.snapshots_path.exists():
			return {}

		def _read() -> dict[str, ProductivityRow]:
			last = ""
			for line in self.snapshots_path.read_text(encoding="utf-8").splitlines():
				if line.strip():
					last = line.strip()
			if not last:
				return {}
			try:
				payload = json.loads(last)
			except json.JSONDecodeError:
				return {}
			fo_payload = payload.get("fo", {}) if isinstance(payload, dict) else {}
			if not isinstance(fo_payload, dict):
				return {}
			result: dict[str, ProductivityRow] = {}
			for fo_name, item in fo_payload.items():
				if not isinstance(item, dict):
					continue
				result[str(fo_name)] = ProductivityRow(
					fo_name=str(fo_name),
					team_name=str(item.get("team", "unknown_team")),
					completed=float(item.get("completed", 0.0)),
					missing=bool(item.get("missing", False)),
				)
			return result

		return await asyncio.to_thread(_read)
