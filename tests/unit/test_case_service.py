"""Tests for case service."""

import pytest
from typing import cast

from src.db.engine import init_db
from src.integrations.surveycto import SurveyCTOClient
from src.models.case import CaseRecord
from src.services.case_service import CaseService
from src.services.escalation_service import EscalationService


class _FakeSurveyForStatus:
	def __init__(self, rows: list[dict[str, str]]) -> None:
		self._rows = rows

	async def fetch_form_wide_csv_rows(self, form_id: str) -> list[dict[str, str]]:
		_ = form_id
		return self._rows

	async def get_case(self, case_id: str) -> CaseRecord:
		return CaseRecord(case_id=case_id, status="open")


class _FakeEscalationService:
	async def create_escalation(
		self,
		requester: str,
		reason: str,
		channel: str,
		case_id: str | None = None,
		question: str | None = None,
	) -> int:
		_ = requester, reason, channel, case_id, question
		return 777


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


@pytest.mark.asyncio
async def test_case_status_reads_closed_from_users_column() -> None:
	"""Closed/refused/team mapping should be driven by cases CSV users column."""

	service = CaseService(
		survey_client=cast(
			SurveyCTOClient,
			_FakeSurveyForStatus([
			{"caseid": "H019412021", "users": "Closed"},
			]),
		),
	)
	status = await service.case_status("H019412021")
	assert "status: closed" in status.lower()


@pytest.mark.asyncio
async def test_case_status_escalates_on_reopen_request() -> None:
	"""Status change requests should generate an escalation entry."""

	service = CaseService(
		survey_client=cast(
			SurveyCTOClient,
			_FakeSurveyForStatus([
				{"caseid": "H019412025", "users": "team_b"},
			]),
		),
		escalation_service=cast(EscalationService, _FakeEscalationService()),
	)
	status = await service.case_status(
		"H019412025",
		requester="123",
		channel="#ops",
		request_text="Please reopen this case and reassign.",
	)
	assert "escalation id" in status.lower()
