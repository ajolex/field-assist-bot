"""Knowledge base indexing utilities."""

from dataclasses import dataclass
from pathlib import Path

from src.integrations.openai_client import OpenAIClient


@dataclass
class KnowledgeChunk:
	"""Indexed chunk with embedding."""

	chunk_id: str
	source_doc: str
	section_path: str
	text: str
	embedding: list[float]


class KnowledgeIndexer:
	"""Builds chunked index from markdown docs."""

	def __init__(self, base_path: Path, openai_client: OpenAIClient) -> None:
		self.base_path = base_path
		self.openai_client = openai_client

	def _chunk_text(self, text: str, size: int = 512, overlap: int = 64) -> list[str]:
		"""Split text into overlapping chunks by characters."""

		if not text.strip():
			return []
		chunks: list[str] = []
		step = max(size - overlap, 1)
		for start in range(0, len(text), step):
			part = text[start : start + size]
			if part:
				chunks.append(part)
		return chunks

	def build_index(self) -> list[KnowledgeChunk]:
		"""Read markdown files and produce embedded chunks."""

		chunks: list[KnowledgeChunk] = []
		for markdown_file in sorted(self.base_path.glob("*.md")):
			content = markdown_file.read_text(encoding="utf-8")
			for index, text in enumerate(self._chunk_text(content)):
				chunk_id = f"{markdown_file.stem}-{index}"
				chunks.append(
					KnowledgeChunk(
						chunk_id=chunk_id,
						source_doc=markdown_file.name,
						section_path="root",
						text=text,
						embedding=self.openai_client.embed_text(text),
					)
				)
		return chunks
