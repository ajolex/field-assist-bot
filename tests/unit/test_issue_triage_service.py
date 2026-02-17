"""Tests for issue triage service."""

from pathlib import Path
from typing import cast

import pytest

from src.integrations.openai_client import OpenAIClient
from src.services.issue_triage_service import IssueTriageService


class _FakeOpenAI:
	async def chat_with_system_prompt(
		self,
		system_prompt: str,
		user_message: str,
		context: str,
	) -> str:
		_ = system_prompt, user_message, context
		return (
			'{"form_name":"ICM Business","variable_name":"q_income","case_id":"H019412021",'
			'"severity":"high","device_info":"Samsung A15","workaround":"Restart Collect"}'
		)


@pytest.mark.asyncio
async def test_create_and_update_issue(tmp_path: Path) -> None:
	"""Should create structured issue, then update and log status."""
	service = IssueTriageService(cast(OpenAIClient, _FakeOpenAI()))
	service.records_path = tmp_path / "issues.json"
	service.status_log_path = tmp_path / "status.jsonl"

	issue = await service.create_issue(
		reporter_id="123",
		source_channel_id="456",
		source_message_id="789",
		description="q_income error for case H019412021 in ICM Business",
		screenshot_urls=["https://example.com/a.png"],
	)
	assert issue.issue_id.startswith("FI-")
	assert issue.form_name == "ICM Business"
	assert issue.status == "open"

	updated = await service.update_status(
		issue_id=issue.issue_id,
		status="in_progress",
		actor="321",
		note="Assigned to FC",
		owner="FC Team A",
	)
	assert updated is not None
	assert updated.status == "in_progress"
	assert updated.owner == "FC Team A"

	history = await service.get_status_history(issue.issue_id)
	assert len(history) >= 2
