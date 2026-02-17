"""Knowledge retriever utilities."""

from src.integrations.openai_client import OpenAIClient, cosine_similarity
from src.knowledge.indexer import KnowledgeChunk


class KnowledgeRetriever:
	"""Retrieves top-k relevant chunks by embedding similarity."""

	def __init__(self, chunks: list[KnowledgeChunk], openai_client: OpenAIClient) -> None:
		self.chunks = chunks
		self.openai_client = openai_client

	async def search(self, question: str, top_k: int = 4) -> list[KnowledgeChunk]:
		"""Return top-k best matching chunks."""

		query_embedding = await self.openai_client.embed_text_async(question)
		scored = [
			(cosine_similarity(query_embedding, chunk.embedding), chunk)
			for chunk in self.chunks
		]
		scored.sort(key=lambda item: item[0], reverse=True)
		return [chunk for _, chunk in scored[:top_k]]
