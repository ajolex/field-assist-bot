"""Passive knowledge candidate collection utilities."""

import asyncio
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass
class KnowledgeCandidate:
	"""Structured candidate extracted from chat messages."""

	candidate_id: str
	captured_at: str
	message_id: int
	author_id: int
	channel_id: int
	content: str


class KnowledgeCollector:
	"""Collects likely knowledge-base-worthy snippets from chat."""

	KEYWORDS = {
		"should",
		"must",
		"always",
		"never",
		"if",
		"when",
		"rule",
		"protocol",
		"escalate",
		"respondent",
		"survey",
		"fo",
		"case",
	}

	def __init__(self, out_path: Path) -> None:
		"""Initialize collector output path."""
		self.out_path = out_path

	def should_capture(self, text: str) -> bool:
		"""Heuristic filter for useful policy/procedure-like content."""
		normalized = " ".join(text.split()).strip().lower()
		if len(normalized) < 35:
			return False
		if normalized.startswith(("/", "!")):
			return False
		if len(normalized) > 1200:
			return False
		keyword_hit = any(word in normalized for word in self.KEYWORDS)
		question_like = "?" in normalized
		return keyword_hit or question_like

	def _clean(self, text: str) -> str:
		"""Normalize message content before storing."""
		text = re.sub(r"<@!?\d+>", "", text)
		text = re.sub(r"<@&\d+>", "", text)
		text = " ".join(text.split())
		return text.strip()

	def build_candidate(
		self,
		*,
		message_id: int,
		author_id: int,
		channel_id: int,
		content: str,
	) -> KnowledgeCandidate:
		"""Create a serializable candidate record."""
		cleaned = self._clean(content)
		digest = hashlib.sha256(cleaned.encode("utf-8")).hexdigest()[:16]
		return KnowledgeCandidate(
			candidate_id=digest,
			captured_at=datetime.now(UTC).isoformat(),
			message_id=message_id,
			author_id=author_id,
			channel_id=channel_id,
			content=cleaned,
		)

	async def persist(self, candidate: KnowledgeCandidate) -> None:
		"""Append candidate to jsonl store asynchronously."""
		await asyncio.to_thread(self._append_jsonl, candidate)

	def _append_jsonl(self, candidate: KnowledgeCandidate) -> None:
		self.out_path.parent.mkdir(parents=True, exist_ok=True)
		with self.out_path.open("a", encoding="utf-8") as handle:
			handle.write(json.dumps(asdict(candidate), ensure_ascii=False) + "\n")
