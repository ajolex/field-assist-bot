"""Repository for announcements."""

from datetime import datetime, timezone

from sqlalchemy import text

from src.db.engine import engine
from src.models.announcement import AnnouncementRecord


class AnnouncementRepository:
	"""Data access for announcement logs."""

	async def create(self, record: AnnouncementRecord) -> None:
		"""Persist announcement log entry."""

		payload = {
			"type": record.type,
			"channel": record.channel,
			"content": record.content,
			"sent_at": (record.sent_at or datetime.now(timezone.utc)).isoformat(),
		}
		async with engine.begin() as conn:
			await conn.execute(
				text(
					"""
					INSERT INTO announcements (type, channel, content, sent_at)
					VALUES (:type, :channel, :content, :sent_at)
					"""
				),
				payload,
			)

	async def count(self) -> int:
		"""Return announcement count."""

		async with engine.begin() as conn:
			result = await conn.execute(text("SELECT COUNT(*) FROM announcements"))
			value = result.scalar_one()
		return int(value)
