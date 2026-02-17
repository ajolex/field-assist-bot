"""Integration-style tests for surveycto client."""

import pytest

from src.integrations.surveycto import SurveyCTOClient


@pytest.mark.asyncio
async def test_get_case_returns_requested_case() -> None:
	"""Case call should preserve requested case id."""

	client = SurveyCTOClient()
	case = await client.get_case("H019412021")
	assert case.case_id == "H019412021"


@pytest.mark.asyncio
async def test_get_form_versions_returns_map() -> None:
	"""Form versions should return a dictionary."""

	client = SurveyCTOClient()
	versions = await client.get_form_versions()
	assert isinstance(versions, dict)
