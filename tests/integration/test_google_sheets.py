"""Integration-style tests for google sheets client."""

import pytest

from src.config import settings
from src.integrations.google_sheets import GoogleSheetsClient


@pytest.mark.asyncio
async def test_read_assignments_returns_rows() -> None:
	"""Assignments should return at least one row."""

	client = GoogleSheetsClient()
	rows = await client.read_assignments()
	assert rows


@pytest.mark.asyncio
async def test_read_productivity_returns_rows() -> None:
	"""Productivity should return sample rows."""

	client = GoogleSheetsClient()
	rows = await client.read_productivity()
	assert rows


@pytest.mark.asyncio
async def test_read_form_versions_from_settings_returns_map_when_configured() -> None:
	"""Form versions should be read from Settings tabs when sheet IDs are configured."""

	if not settings.google_form_hh_survey_sheet_id and not settings.google_form_icm_business_sheet_id:
		pytest.skip("No SurveyCTO form sheet IDs configured for integration test.")

	client = GoogleSheetsClient()
	versions = await client.read_form_versions_from_settings()
	assert isinstance(versions, dict)
