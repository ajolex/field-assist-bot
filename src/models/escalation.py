"""Escalation domain models."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class EscalationStatus(str, Enum):
	"""Lifecycle states for escalations."""

	OPEN = "open"
	RESOLVED = "resolved"
	DISMISSED = "dismissed"


class EscalationRecord(BaseModel):
	"""Escalation object tracked in the database."""

	escalation_id: int | None = None
	case_id: str | None = None
	requester: str
	reason: str
	question: str | None = None
	channel: str
	status: EscalationStatus = EscalationStatus.OPEN
	resolver: str | None = None
	resolution: str | None = None
	created_at: datetime | None = None
	resolved_at: datetime | None = None
