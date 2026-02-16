"""CLI entry point for knowledge base indexing."""

from pathlib import Path

from src.integrations.openai_client import OpenAIClient
from src.knowledge.indexer import KnowledgeIndexer


def main() -> None:
	"""Build and print knowledge base chunk index stats."""

	indexer = KnowledgeIndexer(Path("docs/knowledge_base"), OpenAIClient())
	chunks = indexer.build_index()
	print(f"Indexed {len(chunks)} chunks from docs/knowledge_base")


if __name__ == "__main__":
	main()
