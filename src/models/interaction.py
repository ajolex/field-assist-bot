"""Interaction domain models."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class ConfidenceLevel(str, Enum):
	"""Confidence levels used by RAG responses."""

	HIGH = "high"
	MEDIUM = "medium"
	LOW = "low"


class InteractionRecord(BaseModel):
	"""Logged user interaction with the bot."""

	question: str
	answer: str
	confidence: ConfidenceLevel
	source_docs: list[str]
	escalated: bool
	channel: str
	user_id: str
	created_at: datetime | None = None
