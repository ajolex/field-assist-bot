"""OpenAI client wrappers used by RAG services."""

import hashlib
from math import sqrt


def cosine_similarity(left: list[float], right: list[float]) -> float:
	"""Compute cosine similarity for same-length vectors."""

	if not left or not right or len(left) != len(right):
		return 0.0
	dot = sum(a * b for a, b in zip(left, right, strict=True))
	left_norm = sqrt(sum(a * a for a in left))
	right_norm = sqrt(sum(b * b for b in right))
	if left_norm == 0 or right_norm == 0:
		return 0.0
	return dot / (left_norm * right_norm)


class OpenAIClient:
	"""Minimal abstraction for embeddings and chat completions."""

	def embed_text(self, text: str, dimensions: int = 32) -> list[float]:
		"""Return deterministic embedding fallback for local development."""

		digest = hashlib.sha256(text.encode("utf-8")).digest()
		values = [byte / 255 for byte in digest]
		if dimensions <= len(values):
			return values[:dimensions]
		expanded = values[:]
		while len(expanded) < dimensions:
			expanded.extend(values)
		return expanded[:dimensions]

	async def answer_with_context(self, question: str, context: str) -> str:
		"""Return deterministic context-grounded response placeholder."""

		if not context.strip():
			return "I do not have enough context to answer this confidently."
		return f"Based on the knowledge base context: {context[:400]}"
