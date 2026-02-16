"""Confidence scoring helpers."""

from src.integrations.openai_client import OpenAIClient
from src.knowledge.indexer import KnowledgeChunk
from src.models.interaction import ConfidenceLevel
from src.utils.logger import get_logger


log = get_logger("confidence")


def from_score(score: float) -> ConfidenceLevel:
	"""Map a numeric score in [0, 1] to confidence level."""

	if score >= 0.8:
		return ConfidenceLevel.HIGH
	if score >= 0.5:
		return ConfidenceLevel.MEDIUM
	return ConfidenceLevel.LOW


def score_from_matches(match_count: int, best_similarity: float) -> float:
	"""Compute simple confidence score from retrieval results."""

	quantity = min(match_count / 4, 1.0)
	quality = max(min(best_similarity, 1.0), 0.0)
	return (quantity * 0.4) + (quality * 0.6)


async def assess_confidence(
	question: str,
	answer: str,
	context_chunks: list[KnowledgeChunk],
	openai_client: OpenAIClient,
) -> ConfidenceLevel:
	"""Assess confidence using LLM evaluation of context quality.

	Falls back to numeric heuristic if OpenAI is unavailable.
	"""

	if not openai_client.has_api_key:
		# Fallback to simple heuristic
		best_similarity = 0.9 if context_chunks else 0.0
		score = score_from_matches(len(context_chunks), best_similarity)
		return from_score(score)

	try:
		# Build context summary
		context_summary = "\n\n".join(
			f"[{chunk.source_doc}] {chunk.text[:200]}..." for chunk in context_chunks[:3]
		)

		# Ask LLM to rate confidence
		prompt = f"""Given the following:

Question: {question}

Answer: {answer}

Context used: {context_summary}

Rate the confidence level (HIGH, MEDIUM, or LOW) based on:
- Does the context directly answer the question?
- Is the answer well-supported by the context?
- Are there any uncertainties or gaps?

Respond with ONLY one word: HIGH, MEDIUM, or LOW."""

		response = await openai_client.chat_with_system_prompt(
			system_prompt="You are a confidence assessor. Evaluate how well the context supports the answer.",
			user_message=prompt,
			context="",
		)

		# Parse response
		response_upper = response.strip().upper()
		if "HIGH" in response_upper:
			return ConfidenceLevel.HIGH
		elif "MEDIUM" in response_upper:
			return ConfidenceLevel.MEDIUM
		elif "LOW" in response_upper:
			return ConfidenceLevel.LOW
		else:
			# Fallback if LLM response is unclear
			log.warning("confidence.unclear_response", response=response)
			best_similarity = 0.9 if context_chunks else 0.0
			score = score_from_matches(len(context_chunks), best_similarity)
			return from_score(score)

	except Exception as e:
		log.error("confidence.llm_assessment_failed", error=str(e))
		# Fallback to heuristic
		best_similarity = 0.9 if context_chunks else 0.0
		score = score_from_matches(len(context_chunks), best_similarity)
		return from_score(score)
