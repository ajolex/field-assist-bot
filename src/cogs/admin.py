"""Admin and maintenance commands."""

import json
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands

from src.bot import FieldAssistBot
from src.config import settings
from src.knowledge.indexer import KnowledgeIndexer
from src.knowledge.retriever import KnowledgeRetriever
from src.utils.permissions import SRA_ROLE, has_any_role


class AdminCog(commands.Cog):
	"""Administrative command group."""

	def __init__(self, bot: FieldAssistBot) -> None:
		self.bot = bot

	@app_commands.command(name="ping", description="Health check command")
	async def ping(self, interaction: discord.Interaction) -> None:
		"""Reply with bot heartbeat."""

		await interaction.response.send_message("pong")

	@app_commands.command(name="bot_stats", description="Show high-level bot stats")
	async def show_bot_stats(self, interaction: discord.Interaction) -> None:
		"""Return interaction/escalation counts."""

		await interaction.response.defer()
		interactions = await self.bot.interaction_repository.count()
		open_escalations = await self.bot.escalation_repository.open_count()
		announcements = await self.bot.announcement_repository.count()
		await interaction.followup.send(
			f"Interactions: {interactions}\nOpen escalations: {open_escalations}\nAnnouncements: {announcements}"
		)

	@app_commands.command(name="reload_kb", description="Reload knowledge base index")
	async def reload_kb(self, interaction: discord.Interaction) -> None:
		"""Rebuild in-memory retriever index."""

		member = interaction.user if isinstance(interaction.user, discord.Member) else None
		if not has_any_role(member, {SRA_ROLE}):
			await interaction.response.send_message("insufficient permissions", ephemeral=True)
			return
		await interaction.response.defer()
		indexer = KnowledgeIndexer(
			Path(settings.knowledge_base_path),
			self.bot.openai_client,
			cache_path=Path(settings.knowledge_index_cache_path),
		)
		chunks, stats = await indexer.build_index()
		retriever = KnowledgeRetriever(chunks, self.bot.openai_client)
		self.bot.protocol_service.retriever = retriever
		await interaction.followup.send(
			"Knowledge base reloaded "
			f"({stats.chunk_count} chunks, reused {stats.reused_chunks}, embedded {stats.embedded_chunks})."
		)

	def _load_candidates(self) -> list[dict[str, str]]:
		"""Read passive-learning candidate records from jsonl file."""

		path = Path(settings.knowledge_candidates_path)
		if not path.exists():
			return []
		candidates: list[dict[str, str]] = []
		for line in path.read_text(encoding="utf-8").splitlines():
			line = line.strip()
			if not line:
				continue
			try:
				item = json.loads(line)
				if isinstance(item, dict):
					candidates.append(item)
			except json.JSONDecodeError:
				continue
		return candidates

	@app_commands.command(name="kb_candidates", description="Show recent captured KB candidates")
	@app_commands.describe(limit="How many recent candidates to show (1-20)")
	async def kb_candidates(self, interaction: discord.Interaction, limit: int = 10) -> None:
		"""List recent candidate IDs for promotion."""

		member = interaction.user if isinstance(interaction.user, discord.Member) else None
		if not has_any_role(member, {SRA_ROLE}):
			await interaction.response.send_message("insufficient permissions", ephemeral=True)
			return
		await interaction.response.defer(ephemeral=True)
		rows = self._load_candidates()
		if not rows:
			await interaction.followup.send("No captured knowledge candidates yet.", ephemeral=True)
			return

		n = max(1, min(limit, 20))
		recent = rows[-n:]
		lines: list[str] = []
		for item in reversed(recent):
			candidate_id = str(item.get("candidate_id", "unknown"))
			content = str(item.get("content", "")).replace("\n", " ").strip()
			preview = (content[:110] + "...") if len(content) > 110 else content
			lines.append(f"- `{candidate_id}`: {preview}")
		await interaction.followup.send(
			"Recent knowledge candidates:\n" + "\n".join(lines), ephemeral=True
		)

	@app_commands.command(name="promote_candidate", description="Promote a captured candidate into KB and reindex")
	@app_commands.describe(
		candidate_id="Candidate ID from /kb_candidates",
		target_doc="KB markdown filename (optional, default from settings)",
	)
	async def promote_candidate(
		self,
		interaction: discord.Interaction,
		candidate_id: str,
		target_doc: str | None = None,
	) -> None:
		"""Append approved candidate to KB markdown and refresh retriever."""

		member = interaction.user if isinstance(interaction.user, discord.Member) else None
		if not has_any_role(member, {SRA_ROLE}):
			await interaction.response.send_message("insufficient permissions", ephemeral=True)
			return
		await interaction.response.defer(ephemeral=True)

		rows = self._load_candidates()
		selected = next((item for item in rows if str(item.get("candidate_id", "")) == candidate_id), None)
		if selected is None:
			await interaction.followup.send(f"Candidate `{candidate_id}` not found.", ephemeral=True)
			return

		doc_name = Path(target_doc or settings.knowledge_promotion_doc).name
		if not doc_name.endswith(".md"):
			doc_name += ".md"
		kb_path = Path(settings.knowledge_base_path)
		kb_path.mkdir(parents=True, exist_ok=True)
		target_path = kb_path / doc_name

		existing = target_path.read_text(encoding="utf-8") if target_path.exists() else ""
		if f"candidate_id: {candidate_id}" in existing:
			await interaction.followup.send(
				f"Candidate `{candidate_id}` already promoted in `{doc_name}`.", ephemeral=True
			)
			return

		captured_at = str(selected.get("captured_at", "unknown"))
		author_id = str(selected.get("author_id", "unknown"))
		channel_id = str(selected.get("channel_id", "unknown"))
		content = str(selected.get("content", "")).strip()
		if not content:
			await interaction.followup.send(
				f"Candidate `{candidate_id}` has empty content.", ephemeral=True
			)
			return

		entry = (
			"\n\n## Learned Candidate\n"
			f"<!-- candidate_id: {candidate_id} -->\n"
			f"- captured_at: {captured_at}\n"
			f"- author_id: {author_id}\n"
			f"- channel_id: {channel_id}\n"
			f"- approved_by: {interaction.user.name}\n\n"
			f"{content}\n"
		)
		target_path.write_text(existing + entry, encoding="utf-8")

		indexer = KnowledgeIndexer(
			Path(settings.knowledge_base_path),
			self.bot.openai_client,
			cache_path=Path(settings.knowledge_index_cache_path),
		)
		chunks, stats = await indexer.build_index()
		retriever = KnowledgeRetriever(chunks, self.bot.openai_client)
		self.bot.retriever = retriever
		if self.bot.protocol_service is not None:
			self.bot.protocol_service.retriever = retriever

		await interaction.followup.send(
			"Promoted and reindexed: "
			f"candidate `{candidate_id}` -> `{doc_name}` "
			f"(chunks={stats.chunk_count}, reused={stats.reused_chunks}, embedded={stats.embedded_chunks}).",
			ephemeral=True,
		)

	@app_commands.command(name="set_version", description="Set form version manually")
	async def set_version(self, interaction: discord.Interaction, form: str, version: str) -> None:
		"""Manual form version override placeholder."""

		member = interaction.user if isinstance(interaction.user, discord.Member) else None
		if not has_any_role(member, {SRA_ROLE}):
			await interaction.response.send_message("insufficient permissions", ephemeral=True)
			return
		await interaction.response.send_message(f"Set {form} to version {version} (override recorded).")

	@app_commands.command(name="resolve", description="Resolve escalation")
	async def resolve(self, interaction: discord.Interaction, escalation_id: int, answer: str) -> None:
		"""Resolve escalation and store resolution."""

		member = interaction.user if isinstance(interaction.user, discord.Member) else None
		if not has_any_role(member, {SRA_ROLE}):
			await interaction.response.send_message("insufficient permissions", ephemeral=True)
			return
		await interaction.response.defer()
		updated = await self.bot.escalation_service.resolve(escalation_id, interaction.user.name, answer)
		if updated:
			await interaction.followup.send(f"Escalation {escalation_id} resolved.")
			return
		await interaction.followup.send("Escalation not found.")

	@app_commands.command(name="escalation_stats", description="Show escalation metrics")
	async def escalation_stats(self, interaction: discord.Interaction) -> None:
		"""Return simple escalation metrics."""

		await interaction.response.defer()
		stats = await self.bot.escalation_service.stats()
		await interaction.followup.send(f"Open escalations: {stats['open']}")


async def setup(bot: FieldAssistBot) -> None:
	"""Load cog into bot instance."""

	await bot.add_cog(AdminCog(bot))
