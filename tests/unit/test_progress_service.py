"""Tests for progress service."""

import pytest

from src.integrations.google_sheets import GoogleSheetsClient
from src.services.progress_service import ProgressService


@pytest.mark.asyncio
async def test_completion_rate_calculates_percentage() -> None:
	"""Completion rate should return percentage."""

	service = ProgressService(GoogleSheetsClient())
	assert await service.completion_rate(5, 10) == 50.0


@pytest.mark.asyncio
async def test_completion_rate_handles_zero_total() -> None:
	"""Zero totals should not divide by zero."""

	service = ProgressService(GoogleSheetsClient())
	assert await service.completion_rate(5, 0) == 0.0


@pytest.mark.asyncio
async def test_overall_progress_returns_fields() -> None:
	"""Overall progress should include completed, target, and rate."""

	service = ProgressService(GoogleSheetsClient())
	values = await service.overall_progress()
	assert "completed" in values and "target" in values and "rate" in values
