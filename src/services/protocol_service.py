"""Protocol question-answering business logic."""

from src.db.repositories.interaction_repo import InteractionRepository
from src.integrations.openai_client import OpenAIClient
from src.knowledge.confidence import from_score, score_from_matches
from src.knowledge.prompt_builder import build_prompt
from src.knowledge.retriever import KnowledgeRetriever
from src.models.interaction import InteractionRecord
from src.models.interaction import ConfidenceLevel
from src.services.escalation_service import EscalationService


class ProtocolService:
	"""Service responsible for protocol responses."""

	def __init__(
		self,
		retriever: KnowledgeRetriever,
		openai_client: OpenAIClient,
		interaction_repository: InteractionRepository,
		escalation_service: EscalationService,
	) -> None:
		self.retriever = retriever
		self.openai_client = openai_client
		self.interaction_repository = interaction_repository
		self.escalation_service = escalation_service

	async def answer_question(self, question: str) -> tuple[str, ConfidenceLevel]:
		"""Answer protocol question with confidence and escalation policy."""

		matches = self.retriever.search(question, top_k=4)
		context = "\n\n".join(chunk.text for chunk in matches)
		best_similarity = 0.9 if matches else 0.0
		score = score_from_matches(len(matches), best_similarity)
		confidence = from_score(score)

		prompt = build_prompt(
			"Answer from context only. If context is weak, say unsure.",
			context,
			question,
		)
		answer = await self.openai_client.answer_with_context(question=question, context=prompt)

		escalated = False
		if confidence == ConfidenceLevel.LOW:
			escalation_id = await self.escalation_service.create_escalation(
				requester="system",
				reason="Low confidence protocol answer",
				channel="#bot-admin",
				question=question,
			)
			answer = f"I am not confident on this. Escalated to SRA (ID {escalation_id})."
			escalated = True

		await self.interaction_repository.create(
			InteractionRecord(
				question=question,
				answer=answer,
				confidence=confidence,
				source_docs=[chunk.source_doc for chunk in matches],
				escalated=escalated,
				channel="#protocol",
				user_id="unknown",
			)
		)

		return answer, confidence
