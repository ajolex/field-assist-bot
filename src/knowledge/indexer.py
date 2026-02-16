"""Knowledge base indexing utilities."""

import re
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

	def _parse_markdown_sections(self, content: str) -> list[tuple[str, str]]:
		"""Parse markdown into sections based on headers.

		Returns list of (section_path, text) tuples.
		"""

		sections: list[tuple[str, str]] = []
		current_path: list[str] = []
		current_text: list[str] = []

		lines = content.split("\n")
		for line in lines:
			# Check for markdown headers (## or ###)
			header_match = re.match(r"^(#{2,3})\s+(.+)$", line)
			if header_match:
				# Save previous section if it has content
				if current_text:
					section_path = " > ".join(current_path) if current_path else "root"
					sections.append((section_path, "\n".join(current_text).strip()))
					current_text = []

				# Update path based on header level
				level = len(header_match.group(1))
				header_text = header_match.group(2).strip()

				if level == 2:  # ## Header
					current_path = [header_text]
				elif level == 3:  # ### Sub-header
					if len(current_path) >= 1:
						current_path = [current_path[0], header_text]
					else:
						current_path = [header_text]
			else:
				current_text.append(line)

		# Add final section
		if current_text:
			section_path = " > ".join(current_path) if current_path else "root"
			sections.append((section_path, "\n".join(current_text).strip()))

		return sections

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
			sections = self._parse_markdown_sections(content)

			for section_path, section_text in sections:
				# Sanitize section path for chunk ID
				safe_section_path = section_path.replace(" > ", "__").replace(" ", "_")

				# If section is large, chunk it
				if len(section_text) > 512:
					text_chunks = self._chunk_text(section_text)
					for index, text_chunk in enumerate(text_chunks):
						chunk_id = f"{markdown_file.stem}-{safe_section_path}-{index}"
						chunks.append(
							KnowledgeChunk(
								chunk_id=chunk_id,
								source_doc=markdown_file.name,
								section_path=section_path,
								text=text_chunk,
								embedding=self.openai_client.embed_text(text_chunk),
							)
						)
				else:
					# Section is small enough, use as-is
					chunk_id = f"{markdown_file.stem}-{safe_section_path}"
					chunks.append(
						KnowledgeChunk(
							chunk_id=chunk_id,
							source_doc=markdown_file.name,
							section_path=section_path,
							text=section_text,
							embedding=self.openai_client.embed_text(section_text),
						)
					)
		return chunks
