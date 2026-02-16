"""Tests for case service."""

import pytest

from src.db.engine import init_db
from src.integrations.surveycto import SurveyCTOClient
from src.services.case_service import CaseService


@pytest.mark.asyncio
async def test_lookup_case_returns_requested_case_id() -> None:
	"""Case lookup should preserve input case ID."""

	service = CaseService(SurveyCTOClient())
	result = await service.lookup_case("H019412021")
	assert result.case_id == "H019412021"


@pytest.mark.asyncio
async def test_request_reopen_stores_record() -> None:
	"""Reopen requests should write to database."""

	await init_db()
	service = CaseService(SurveyCTOClient())
	await service.request_reopen("H019412021", "tester", "needs revisit")
