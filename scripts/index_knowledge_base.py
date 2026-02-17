"""CLI entry point for knowledge base indexing."""

import argparse
import asyncio
from pathlib import Path

from src.config import settings
from src.integrations.openai_client import OpenAIClient
from src.knowledge.indexer import KnowledgeIndexer


async def _run(force_rebuild: bool) -> None:
	"""Build and print knowledge base chunk index stats."""

	indexer = KnowledgeIndexer(
		Path(settings.knowledge_base_path),
		OpenAIClient(),
		cache_path=Path(settings.knowledge_index_cache_path),
	)
	chunks, stats = await indexer.build_index(force_rebuild=force_rebuild)
	print(
		"Knowledge index ready: "
		f"chunks={stats.chunk_count}, docs={stats.total_docs}, "
		f"reused={stats.reused_chunks}, embedded={stats.embedded_chunks}, "
		f"changed_docs={stats.changed_docs}, cache_hit={stats.cache_hit}, "
		f"cache={Path(settings.knowledge_index_cache_path)}"
	)
	if not chunks:
		print("Warning: no chunks were indexed.")


def main() -> None:
	"""Parse args and run index build."""

	parser = argparse.ArgumentParser(description="Build knowledge index cache.")
	parser.add_argument(
		"--force",
		action="store_true",
		help="Force full re-embedding of all markdown docs.",
	)
	args = parser.parse_args()
	asyncio.run(_run(force_rebuild=args.force))


if __name__ == "__main__":
	main()
