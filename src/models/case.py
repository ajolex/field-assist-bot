"""Case domain models."""

from datetime import datetime

from pydantic import BaseModel
from pydantic import Field


class CaseRecord(BaseModel):
	"""Normalized case record used by service layers."""

	case_id: str
	status: str
	team: str | None = None
	barangay: str | None = None
	municipality: str | None = None
	province: str | None = None
	forms: list[str] = Field(default_factory=list)
	treatment: str | None = None
	updated_at: datetime | None = None
