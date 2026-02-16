"""CLI entry point for seeding initial database data."""

import asyncio

from src.db.engine import init_db


async def run() -> None:
	"""Initialize database schema."""

	await init_db()
	print("Database initialized.")


def main() -> None:
	"""Run seed routine."""

	asyncio.run(run())


if __name__ == "__main__":
	main()
