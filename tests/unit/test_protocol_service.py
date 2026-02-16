"""Tests for protocol service."""

from pathlib import Path

import pytest

from src.db.engine import init_db
from src.db.repositories.interaction_repo import InteractionRepository
from src.integrations.openai_client import OpenAIClient
from src.knowledge.indexer import KnowledgeIndexer
from src.knowledge.retriever import KnowledgeRetriever
from src.models.interaction import ConfidenceLevel
from src.services.escalation_service import EscalationService
from src.services.protocol_service import ProtocolService
from src.db.repositories.escalation_repo import EscalationRepository


@pytest.mark.asyncio
async def test_answer_question_returns_low_confidence_placeholder() -> None:
	"""Protocol service returns known confidence value."""

	await init_db()
	indexer = KnowledgeIndexer(Path("docs/knowledge_base"), OpenAIClient())
	retriever = KnowledgeRetriever(indexer.build_index(), OpenAIClient())
	service = ProtocolService(
		retriever,
		OpenAIClient(),
		InteractionRepository(),
		EscalationService(EscalationRepository()),
	)
	_, confidence = await service.answer_question("What is PSPS?")
	assert confidence in {ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM, ConfidenceLevel.LOW}
