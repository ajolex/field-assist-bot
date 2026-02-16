"""Escalation lifecycle business logic."""

from src.db.repositories.escalation_repo import EscalationRepository
from src.models.escalation import EscalationRecord


class EscalationService:
	"""Creates, resolves, and reports escalations."""

	def __init__(self, repository: EscalationRepository) -> None:
		self.repository = repository

	async def create_escalation(
		self,
		requester: str,
		reason: str,
		channel: str,
		case_id: str | None = None,
		question: str | None = None,
	) -> int:
		"""Create and return escalation ID."""

		return await self.repository.create(
			EscalationRecord(
				requester=requester,
				reason=reason,
				channel=channel,
				case_id=case_id,
				question=question,
			)
		)

	async def resolve(self, escalation_id: int, resolver: str, resolution: str) -> bool:
		"""Resolve escalation by ID."""

		return await self.repository.resolve(escalation_id, resolver, resolution)

	async def stats(self) -> dict[str, int]:
		"""Return escalation metrics."""

		return {"open": await self.repository.open_count()}
