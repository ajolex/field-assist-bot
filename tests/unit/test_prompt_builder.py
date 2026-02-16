"""Tests for prompt builder."""

from src.knowledge.indexer import KnowledgeChunk
from src.knowledge.prompt_builder import build_prompt


def test_build_prompt_contains_all_sections() -> None:
	"""Prompt should include system prompt, context, and question."""

	chunks = [
		KnowledgeChunk(
			chunk_id="test-1",
			source_doc="test.md",
			section_path="Test Section",
			text="Test context text",
			embedding=[0.1, 0.2],
		)
	]
	messages = build_prompt("What is the test?", chunks)

	# Check that we have the expected message structure
	assert len(messages) == 3
	assert messages[0]["role"] == "system"
	assert "Field Assist Bot" in messages[0]["content"]
	assert messages[1]["role"] == "system"
	assert "Context from knowledge base" in messages[1]["content"]
	assert messages[2]["role"] == "user"
	assert messages[2]["content"] == "What is the test?"
