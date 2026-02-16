"""E2E-style tests for command registration surface."""

from src.bot import COGS


def test_expected_cogs_are_registered() -> None:
	"""Bot should load all key cogs defined in the implementation plan."""

	assert "src.cogs.cases" in COGS
	assert "src.cogs.protocol" in COGS
	assert "src.cogs.progress" in COGS
	assert "src.cogs.admin" in COGS
