"""Form version domain models."""

from datetime import datetime

from pydantic import BaseModel


class FormVersionRecord(BaseModel):
	"""Tracks detected form versions."""

	form_id: str
	version: str
	detected_at: datetime | None = None
	announced: bool = False
