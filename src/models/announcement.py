"""Announcement domain models."""

from datetime import datetime

from pydantic import BaseModel


class AnnouncementRecord(BaseModel):
	"""A sent announcement event."""

	announcement_id: int | None = None
	type: str
	channel: str
	content: str
	sent_at: datetime | None = None
