"""Repository for escalation records."""

from datetime import datetime, timezone

from sqlalchemy import text

from src.db.engine import engine
from src.models.escalation import EscalationRecord, EscalationStatus


class EscalationRepository:
	"""Data access for escalation lifecycle."""

	async def create(self, record: EscalationRecord) -> int:
		"""Insert escalation and return generated ID."""

		payload = {
			"case_id": record.case_id,
			"requester": record.requester,
			"reason": record.reason,
			"question": record.question,
			"channel": record.channel,
			"status": record.status.value,
			"resolver": record.resolver,
			"resolution": record.resolution,
			"created_at": (record.created_at or datetime.now(timezone.utc)).isoformat(),
			"resolved_at": record.resolved_at.isoformat() if record.resolved_at else None,
		}
		async with engine.begin() as conn:
			result = await conn.execute(
				text(
					"""
					INSERT INTO escalations (case_id, requester, reason, question, channel, status, resolver, resolution, created_at, resolved_at)
					VALUES (:case_id, :requester, :reason, :question, :channel, :status, :resolver, :resolution, :created_at, :resolved_at)
					"""
				),
				payload,
			)
			escalation_id = result.lastrowid
		if escalation_id is None:
			raise RuntimeError("Failed to create escalation record")
		return int(escalation_id)

	async def resolve(self, escalation_id: int, resolver: str, resolution: str) -> bool:
		"""Resolve escalation by ID."""

		payload = {
			"id": escalation_id,
			"status": EscalationStatus.RESOLVED.value,
			"resolver": resolver,
			"resolution": resolution,
			"resolved_at": datetime.now(timezone.utc).isoformat(),
		}
		async with engine.begin() as conn:
			result = await conn.execute(
				text(
					"""
					UPDATE escalations
					SET status = :status, resolver = :resolver, resolution = :resolution, resolved_at = :resolved_at
					WHERE id = :id
					"""
				),
				payload,
			)
		return result.rowcount > 0

	async def open_count(self) -> int:
		"""Return open escalation count."""

		async with engine.begin() as conn:
			result = await conn.execute(
				text("SELECT COUNT(*) FROM escalations WHERE status = :status"),
				{"status": EscalationStatus.OPEN.value},
			)
			value = result.scalar_one()
		return int(value)
