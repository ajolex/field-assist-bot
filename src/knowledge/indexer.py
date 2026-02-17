"""Knowledge base indexing utilities."""

import hashlib
import pickle
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.config import settings
from src.integrations.openai_client import OpenAIClient


@dataclass
class KnowledgeChunk:
	"""Indexed chunk with embedding."""

	chunk_id: str
	source_doc: str
	section_path: str
	text: str
	embedding: list[float]


@dataclass
class KnowledgeIndexStats:
	"""Operational stats for index build/load."""

	total_docs: int
	chunk_count: int
	reused_chunks: int
	embedded_chunks: int
	changed_docs: int
	cache_hit: bool


class KnowledgeIndexer:
	"""Builds chunked index from markdown docs."""

	def __init__(
		self,
		base_path: Path,
		openai_client: OpenAIClient,
		cache_path: Path | None = None,
	) -> None:
		self.base_path = base_path
		self.openai_client = openai_client
		self.cache_path = cache_path or Path(settings.knowledge_index_cache_path)

	def _file_hash(self, path: Path) -> str:
		"""Compute SHA256 hash for change detection."""

		hasher = hashlib.sha256()
		with path.open("rb") as handle:
			for block in iter(lambda: handle.read(65536), b""):
				hasher.update(block)
		return hasher.hexdigest()

	def _load_cache(self) -> dict[str, Any] | None:
		"""Load persisted index cache if available."""

		if not self.cache_path.exists():
			return None
		try:
			with self.cache_path.open("rb") as handle:
				data: dict[str, Any] = pickle.load(handle)
			return data
		except Exception:
			return None

	def _save_cache(self, payload: dict[str, Any]) -> None:
		"""Persist index cache to disk."""

		self.cache_path.parent.mkdir(parents=True, exist_ok=True)
		with self.cache_path.open("wb") as handle:
			pickle.dump(payload, handle, protocol=pickle.HIGHEST_PROTOCOL)

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

	def _relative_doc_path(self, path: Path) -> str:
		"""Return stable document key relative to KB root."""

		return path.relative_to(self.base_path).as_posix()

	async def build_index(self, force_rebuild: bool = False) -> tuple[list[KnowledgeChunk], KnowledgeIndexStats]:
		"""Read markdown files and produce embedded chunks with incremental cache reuse."""

		markdown_files = sorted(self.base_path.rglob("*.md"), key=lambda item: item.as_posix())
		current_hashes = {self._relative_doc_path(path): self._file_hash(path) for path in markdown_files}

		cache = None if force_rebuild else self._load_cache()
		cache_model = cache.get("embedding_model") if cache else None
		cache_hashes: dict[str, str] = cache.get("doc_hashes", {}) if cache else {}
		cache_chunks: list[KnowledgeChunk] = cache.get("chunks", []) if cache else []

		if cache and cache_model == settings.openai_embedding_model and cache_hashes == current_hashes:
			stats = KnowledgeIndexStats(
				total_docs=len(markdown_files),
				chunk_count=len(cache_chunks),
				reused_chunks=len(cache_chunks),
				embedded_chunks=0,
				changed_docs=0,
				cache_hit=True,
			)
			return cache_chunks, stats

		reusable_by_doc: dict[str, list[KnowledgeChunk]] = {}
		if cache and cache_model == settings.openai_embedding_model:
			for chunk in cache_chunks:
				reusable_by_doc.setdefault(chunk.source_doc, []).append(chunk)

		# Collect all chunk metadata first, then batch-embed
		pending: list[tuple[str, str, str, str]] = []  # (chunk_id, source_doc, section_path, text)
		reused_chunks: list[KnowledgeChunk] = []
		changed_docs = 0

		for markdown_file in markdown_files:
			file_name = self._relative_doc_path(markdown_file)
			if (
				not force_rebuild
				and cache_model == settings.openai_embedding_model
				and cache_hashes.get(file_name) == current_hashes[file_name]
				and file_name in reusable_by_doc
			):
				reused_chunks.extend(reusable_by_doc[file_name])
				continue

			changed_docs += 1
			content = markdown_file.read_text(encoding="utf-8")
			sections = self._parse_markdown_sections(content)

			for section_path, section_text in sections:
				safe_section_path = section_path.replace(" > ", "__").replace(" ", "_")
				safe_doc_key = re.sub(r"[^a-zA-Z0-9_-]+", "_", file_name)

				if len(section_text) > 512:
					text_chunks = self._chunk_text(section_text)
					for index, text_chunk in enumerate(text_chunks):
						chunk_id = f"{safe_doc_key}-{safe_section_path}-{index}"
						pending.append((chunk_id, file_name, section_path, text_chunk))
				else:
					chunk_id = f"{safe_doc_key}-{safe_section_path}"
					pending.append((chunk_id, file_name, section_path, section_text))

		# Batch embed only changed/new texts
		texts = [text for _, _, _, text in pending]
		all_embeddings = await self.openai_client.embed_batch_async(texts) if texts else []

		new_chunks: list[KnowledgeChunk] = []
		for (chunk_id, source_doc, section_path, text), embedding in zip(pending, all_embeddings, strict=True):
			new_chunks.append(
				KnowledgeChunk(
					chunk_id=chunk_id,
					source_doc=source_doc,
					section_path=section_path,
					text=text,
					embedding=embedding,
				)
			)

		chunks = reused_chunks + new_chunks
		chunks.sort(key=lambda chunk: chunk.chunk_id)

		self._save_cache(
			{
				"embedding_model": settings.openai_embedding_model,
				"doc_hashes": current_hashes,
				"chunks": chunks,
			}
		)

		stats = KnowledgeIndexStats(
			total_docs=len(markdown_files),
			chunk_count=len(chunks),
			reused_chunks=len(reused_chunks),
			embedded_chunks=len(new_chunks),
			changed_docs=changed_docs,
			cache_hit=False,
		)
		return chunks, stats
