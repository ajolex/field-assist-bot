"""Async SQLAlchemy engine and session factory."""

from collections.abc import AsyncIterator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import settings

engine = create_async_engine(settings.database_url, echo=False)
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncIterator[AsyncSession]:
	"""Yield an async database session."""
	async with SessionLocal() as session:
		yield session


async def init_db() -> None:
	"""Initialize required tables for bot operation."""
	ddl_statements = [
		"""
		CREATE TABLE IF NOT EXISTS interactions (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			question TEXT NOT NULL,
			answer TEXT NOT NULL,
			confidence TEXT NOT NULL,
			source_docs TEXT NOT NULL,
			escalated INTEGER NOT NULL,
			channel TEXT NOT NULL,
			user_id TEXT NOT NULL,
			created_at TEXT NOT NULL
		)
		""",
		"""
		CREATE TABLE IF NOT EXISTS escalations (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			case_id TEXT,
			requester TEXT NOT NULL,
			reason TEXT NOT NULL,
			question TEXT,
			channel TEXT NOT NULL,
			status TEXT NOT NULL,
			resolver TEXT,
			resolution TEXT,
			created_at TEXT NOT NULL,
			resolved_at TEXT
		)
		""",
		"""
		CREATE TABLE IF NOT EXISTS announcements (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			type TEXT NOT NULL,
			channel TEXT NOT NULL,
			content TEXT NOT NULL,
			sent_at TEXT NOT NULL
		)
		""",
		"""
		CREATE TABLE IF NOT EXISTS form_versions (
			form_id TEXT PRIMARY KEY,
			version TEXT NOT NULL,
			detected_at TEXT NOT NULL,
			announced INTEGER NOT NULL
		)
		""",
		"""
		CREATE TABLE IF NOT EXISTS reopen_requests (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			case_id TEXT NOT NULL,
			requester TEXT NOT NULL,
			reason TEXT NOT NULL,
			status TEXT NOT NULL,
			created_at TEXT NOT NULL
		)
		""",
	]

	async with engine.begin() as conn:
		for ddl in ddl_statements:
			await conn.execute(text(ddl))
