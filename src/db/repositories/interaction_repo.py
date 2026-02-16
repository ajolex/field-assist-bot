"""Repository for interaction logs."""

import json
from datetime import datetime, timezone

from sqlalchemy import text

from src.db.engine import engine
from src.models.interaction import InteractionRecord


class InteractionRepository:
	"""Data access for interaction records."""

	async def create(self, record: InteractionRecord) -> None:
		"""Insert a new interaction."""

		payload = {
			"question": record.question,
			"answer": record.answer,
			"confidence": record.confidence.value,
			"source_docs": json.dumps(record.source_docs),
			"escalated": 1 if record.escalated else 0,
			"channel": record.channel,
			"user_id": record.user_id,
			"created_at": (record.created_at or datetime.now(timezone.utc)).isoformat(),
		}
		async with engine.begin() as conn:
			await conn.execute(
				text(
					"""
					INSERT INTO interactions (question, answer, confidence, source_docs, escalated, channel, user_id, created_at)
					VALUES (:question, :answer, :confidence, :source_docs, :escalated, :channel, :user_id, :created_at)
					"""
				),
				payload,
			)

	async def count(self) -> int:
		"""Return interaction count."""

		async with engine.begin() as conn:
			result = await conn.execute(text("SELECT COUNT(*) FROM interactions"))
			value = result.scalar_one()
		return int(value)
