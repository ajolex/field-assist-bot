"""Tests for progress exceptions service."""

from pathlib import Path
from typing import cast

import pytest

from src.integrations.google_sheets import GoogleSheetsClient
from src.services.progress_exceptions_service import ProgressExceptionsService


class _FakeSheets:
	def __init__(self, rows: list[dict[str, str]]) -> None:
		self._rows = rows

	async def read_productivity(self) -> list[dict[str, str]]:
		return self._rows


@pytest.mark.asyncio
async def test_build_nightly_report_detects_anomalies(tmp_path: Path) -> None:
	"""Should detect under-target, lagging team, and missing report."""
	rows = [
		{"fo": "FO-1", "team": "team_a", "completed": "1"},
		{"fo": "FO-2", "team": "team_a", "completed": ""},
		{"fo": "FO-3", "team": "team_b", "completed": "4"},
	]
	service = ProgressExceptionsService(cast(GoogleSheetsClient, _FakeSheets(rows)))
	service.snapshots_path = tmp_path / "snapshots.jsonl"

	report = await service.build_nightly_report()
	assert report.has_anomalies is True
	assert "Under-target FOs" in report.text
	assert "Missing Reports" in report.text
