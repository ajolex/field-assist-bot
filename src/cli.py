"""Command-line utilities for running the Field Assist Bot."""

import argparse
import asyncio
from pathlib import Path

from src.bot import start_bot
from src.config import settings
from src.integrations.openai_client import OpenAIClient
from src.knowledge.indexer import KnowledgeIndexer


async def _run_index(force_rebuild: bool) -> None:
	"""Build and print knowledge index stats before bot startup."""

	indexer = KnowledgeIndexer(
		Path(settings.knowledge_base_path),
		OpenAIClient(),
		cache_path=Path(settings.knowledge_index_cache_path),
	)
	_, stats = await indexer.build_index(force_rebuild=force_rebuild)
	print(
		"Knowledge index ready: "
		f"chunks={stats.chunk_count}, docs={stats.total_docs}, "
		f"reused={stats.reused_chunks}, embedded={stats.embedded_chunks}, "
		f"changed_docs={stats.changed_docs}, cache_hit={stats.cache_hit}"
	)


async def _run(index_first: bool, force_index: bool) -> None:
	"""Optionally index docs, then launch the bot."""

	if index_first:
		await _run_index(force_rebuild=force_index)
	await start_bot()


def run_bot() -> None:
	"""Entry point: index knowledge base first, then run bot."""

	parser = argparse.ArgumentParser(
		description="Run Field Assist Bot from terminal with optional indexing."
	)
	parser.add_argument(
		"--skip-index",
		action="store_true",
		help="Skip pre-start knowledge indexing.",
	)
	parser.add_argument(
		"--force-index",
		action="store_true",
		help="Force full re-embedding when indexing runs.",
	)
	args = parser.parse_args()
	asyncio.run(_run(index_first=not args.skip_index, force_index=args.force_index))


def index_only() -> None:
	"""Entry point: only build knowledge index, do not start bot."""

	parser = argparse.ArgumentParser(description="Build knowledge index cache.")
	parser.add_argument(
		"--force",
		action="store_true",
		help="Force full re-embedding of all markdown docs.",
	)
	args = parser.parse_args()
	asyncio.run(_run_index(force_rebuild=args.force))


if __name__ == "__main__":
	run_bot()
