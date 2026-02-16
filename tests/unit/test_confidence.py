"""Tests for confidence model contract."""

from src.models.interaction import ConfidenceLevel


def test_confidence_levels_match_contract() -> None:
	"""Enum values must match shared interface contract."""

	assert ConfidenceLevel.HIGH.value == "high"
	assert ConfidenceLevel.MEDIUM.value == "medium"
	assert ConfidenceLevel.LOW.value == "low"
