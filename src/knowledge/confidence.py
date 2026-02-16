"""Confidence scoring helpers."""

from src.models.interaction import ConfidenceLevel


def from_score(score: float) -> ConfidenceLevel:
	"""Map a numeric score in [0, 1] to confidence level."""

	if score >= 0.8:
		return ConfidenceLevel.HIGH
	if score >= 0.5:
		return ConfidenceLevel.MEDIUM
	return ConfidenceLevel.LOW


def score_from_matches(match_count: int, best_similarity: float) -> float:
	"""Compute simple confidence score from retrieval results."""

	quantity = min(match_count / 4, 1.0)
	quality = max(min(best_similarity, 1.0), 0.0)
	return (quantity * 0.4) + (quality * 0.6)
