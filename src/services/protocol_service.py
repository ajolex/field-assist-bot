"""Protocol question-answering business logic."""

from src.db.repositories.interaction_repo import InteractionRepository
from src.integrations.openai_client import OpenAIClient
from src.knowledge.confidence import assess_confidence
from src.knowledge.prompt_builder import build_prompt
from src.knowledge.retriever import KnowledgeRetriever
from src.models.interaction import ConfidenceLevel, InteractionRecord
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

	async def answer_question(
		self, question: str, user_id: str = "unknown", channel: str = "#protocol"
	) -> tuple[str, ConfidenceLevel]:
		"""Answer protocol question with full RAG pipeline.

		Pipeline:
		1. Retrieve relevant chunks from knowledge base
		2. Build prompt with system prompt, context, and question
		3. Call LLM to generate answer
		4. Assess confidence level
		5. Apply escalation rules
		6. Log interaction
		7. Return answer and confidence
		"""

		# Step 1: Retrieve relevant chunks
		matches = self.retriever.search(question, top_k=4)

		# Step 2: Build prompt
		messages = build_prompt(question, matches)

		# Step 3: Generate answer
		# Extract context for the chat call
		context_text = "\n\n".join(
			f"[{chunk.source_doc}] {chunk.text}" for chunk in matches
		)

		answer = await self.openai_client.chat_with_system_prompt(
			system_prompt=messages[0]["content"],  # System prompt
			user_message=question,
			context=context_text,
		)

		# Step 4: Assess confidence
		confidence = await assess_confidence(question, answer, matches, self.openai_client)

		# Step 5: Apply escalation rules
		escalated = False
		if confidence == ConfidenceLevel.LOW:
			escalation_id = await self.escalation_service.create_escalation(
				requester=user_id,
				reason="Low confidence protocol answer",
				channel=channel,
				question=question,
			)
			answer = (
				f"I am not confident about this answer. I've escalated this to the "
				f"Senior Research Associate for review (Escalation ID: {escalation_id}).\n\n"
				f"Preliminary context: {answer[:200]}"
			)
			escalated = True
		elif confidence == ConfidenceLevel.MEDIUM:
			answer = (
				f"{answer}\n\n⚠️ *Medium confidence* - Please verify with the "
				"Senior Research Associate if critical."
			)

		# Include source document references
		if matches:
			sources = list({chunk.source_doc for chunk in matches})
			source_text = ", ".join(sources)
			answer += f"\n\n📚 Sources: {source_text}"

		# Step 6: Log interaction
		await self.interaction_repository.create(
			InteractionRecord(
				question=question,
				answer=answer,
				confidence=confidence,
				source_docs=[chunk.source_doc for chunk in matches],
				escalated=escalated,
				channel=channel,
				user_id=user_id,
			)
		)

		return answer, confidence
