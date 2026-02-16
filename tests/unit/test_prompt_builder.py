"""Tests for prompt builder."""

from src.knowledge.prompt_builder import build_prompt


def test_build_prompt_contains_all_sections() -> None:
	"""Prompt should include system, context, and question sections."""

	prompt = build_prompt("sys", "ctx", "q", history=["h1", "h2"])
	assert "System:" in prompt
	assert "History:" in prompt
	assert "Context:" in prompt
	assert "User Question:" in prompt
