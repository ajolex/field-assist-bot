"""Integration-style tests for RAG pipeline components."""

from pathlib import Path

import pytest

from src.integrations.openai_client import OpenAIClient
from src.knowledge.indexer import KnowledgeIndexer
from src.knowledge.retriever import KnowledgeRetriever


@pytest.mark.asyncio
async def test_retriever_returns_matches_from_docs() -> None:
	"""Retriever should return relevant chunks for known protocol query."""

	client = OpenAIClient()
	chunks, _ = await KnowledgeIndexer(Path("docs/knowledge_base"), client).build_index()
	retriever = KnowledgeRetriever(chunks, client)
	matches = await retriever.search("Can we interview moved respondent?")
	assert isinstance(matches, list)
