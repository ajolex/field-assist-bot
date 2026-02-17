"""OpenAI client wrappers used by RAG services."""

import asyncio
import hashlib
from math import sqrt

from openai import AsyncOpenAI, APIError, BadRequestError, RateLimitError

from src.config import settings
from src.utils.logger import get_logger


log = get_logger("openai_client")


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

	def __init__(self) -> None:
		self.has_api_key = bool(settings.openai_api_key)
		if self.has_api_key:
			self.client = AsyncOpenAI(api_key=settings.openai_api_key)
			log.info("openai.initialized", has_key=True)
		else:
			log.warning("openai.no_key", message="Using deterministic fallback embeddings")

	def _deterministic_embed(self, text: str, dimensions: int = 32) -> list[float]:
		"""Return deterministic embedding fallback for local development."""

		digest = hashlib.sha256(text.encode("utf-8")).digest()
		values = [byte / 255 for byte in digest]
		if dimensions <= len(values):
			return values[:dimensions]
		expanded = values[:]
		while len(expanded) < dimensions:
			expanded.extend(values)
		return expanded[:dimensions]

	def embed_text(self, text: str, dimensions: int = 32) -> list[float]:
		"""Generate text embedding synchronously (for indexing)."""

		if not self.has_api_key:
			return self._deterministic_embed(text, dimensions)

		# For sync context (indexing), use asyncio.run
		try:
			loop = asyncio.get_event_loop()
			if loop.is_running():
				# If we're in an async context, fall back to deterministic
				return self._deterministic_embed(text, dimensions)
			return loop.run_until_complete(self._embed_text_async(text))
		except RuntimeError:
			# No event loop, create one
			return asyncio.run(self._embed_text_async(text))

	async def _embed_text_async(self, text: str) -> list[float]:
		"""Generate text embedding using OpenAI API."""

		try:
			response = await self.client.embeddings.create(
				model=settings.openai_embedding_model,
				input=text,
			)
			return response.data[0].embedding
		except (APIError, RateLimitError) as e:
			log.error("openai.embed_error", error=str(e))
			return self._deterministic_embed(text, 32)

	async def embed_text_async(self, text: str, dimensions: int = 32) -> list[float]:
		"""Async-safe embedding method for use within a running event loop."""

		if not self.has_api_key:
			return self._deterministic_embed(text, dimensions)
		return await self._embed_text_async(text)

	async def embed_batch_async(self, texts: list[str]) -> list[list[float]]:
		"""Embed multiple texts in batches via the OpenAI API."""

		if not self.has_api_key or not texts:
			return [self._deterministic_embed(t, 32) for t in texts]

		# Replace empty/whitespace-only strings — OpenAI rejects them
		cleaned: list[str] = [t.strip() if t.strip() else "empty" for t in texts]

		all_embeddings: list[list[float]] = []
		BATCH = 50
		for i in range(0, len(cleaned), BATCH):
			batch = cleaned[i : i + BATCH]
			try:
				response = await self.client.embeddings.create(
					model=settings.openai_embedding_model,
					input=batch,
				)
				all_embeddings.extend(item.embedding for item in response.data)
			except Exception as e:
				log.error("openai.batch_embed_error", error=str(e), batch_start=i, batch_size=len(batch))
				all_embeddings.extend(self._deterministic_embed(t, 32) for t in batch)

		return all_embeddings

	async def answer_with_context(self, question: str, context: str) -> str:
		"""Return context-grounded response using chat completions."""

		if not self.has_api_key:
			if not context.strip():
				return "I do not have enough context to answer this confidently."
			return f"Based on the knowledge base context: {context[:400]}"

		try:
			response = await self.client.chat.completions.create(
				model=settings.openai_model_primary,
				messages=[
					{
						"role": "system",
						"content": "You are a helpful assistant. Answer only from the provided context.",
					},
					{"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
				],
				temperature=0.3,
			)
			return response.choices[0].message.content or "No response generated."
		except (APIError, RateLimitError) as e:
			log.warning("openai.primary_model_failed", error=str(e), trying_fallback=True)
			try:
				response = await self.client.chat.completions.create(
					model=settings.openai_model_fallback,
					messages=[
						{
							"role": "system",
							"content": "You are a helpful assistant. Answer only from the provided context.",
						},
						{"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
					],
					temperature=0.3,
				)
				return response.choices[0].message.content or "No response generated."
			except (APIError, RateLimitError) as fallback_error:
				log.error("openai.fallback_model_failed", error=str(fallback_error))
				if not context.strip():
					return "I do not have enough context to answer this confidently."
				return f"Based on the knowledge base context: {context[:400]}"

	async def chat_with_system_prompt(
		self, system_prompt: str, user_message: str, context: str
	) -> str:
		"""Assemble chat completion with system prompt, context, and user question."""

		if not self.has_api_key:
			if not context.strip():
				return "I do not have enough context to answer this confidently."
			return f"Based on the knowledge base context: {context[:400]}"

		messages = [
			{"role": "system", "content": system_prompt},
			{"role": "system", "content": f"Context from knowledge base:\n{context}"},
			{"role": "user", "content": user_message},
		]

		try:
			response = await self.client.chat.completions.create(
				model=settings.openai_model_primary,
				messages=messages,
				temperature=0.3,
			)
			return response.choices[0].message.content or "No response generated."
		except (APIError, RateLimitError) as e:
			log.warning("openai.primary_model_failed", error=str(e), trying_fallback=True)
			try:
				response = await self.client.chat.completions.create(
					model=settings.openai_model_fallback,
					messages=messages,
					temperature=0.3,
				)
				return response.choices[0].message.content or "No response generated."
			except (APIError, RateLimitError) as fallback_error:
				log.error("openai.fallback_model_failed", error=str(fallback_error))
				if not context.strip():
					return "I do not have enough context to answer this confidently."
				return f"Based on the knowledge base context: {context[:400]}"
