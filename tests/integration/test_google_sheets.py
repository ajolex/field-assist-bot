"""Integration-style tests for google sheets client."""

import pytest

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
