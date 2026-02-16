"""Admin and maintenance commands."""

from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands

from src.bot import FieldAssistBot
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
	async def bot_stats(self, interaction: discord.Interaction) -> None:
		"""Return interaction/escalation counts."""

		interactions = await self.bot.interaction_repository.count()
		open_escalations = await self.bot.escalation_repository.open_count()
		announcements = await self.bot.announcement_repository.count()
		await interaction.response.send_message(
			f"Interactions: {interactions}\nOpen escalations: {open_escalations}\nAnnouncements: {announcements}"
		)

	@app_commands.command(name="reload_kb", description="Reload knowledge base index")
	async def reload_kb(self, interaction: discord.Interaction) -> None:
		"""Rebuild in-memory retriever index."""

		member = interaction.user if isinstance(interaction.user, discord.Member) else None
		if not has_any_role(member, {SRA_ROLE}):
			await interaction.response.send_message("insufficient permissions", ephemeral=True)
			return
		indexer = KnowledgeIndexer(Path("docs/knowledge_base"), self.bot.openai_client)
		retriever = KnowledgeRetriever(indexer.build_index(), self.bot.openai_client)
		self.bot.protocol_service.retriever = retriever
		await interaction.response.send_message("Knowledge base reloaded.")

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
		updated = await self.bot.escalation_service.resolve(escalation_id, interaction.user.name, answer)
		if updated:
			await interaction.response.send_message(f"Escalation {escalation_id} resolved.")
			return
		await interaction.response.send_message("Escalation not found.")

	@app_commands.command(name="escalation_stats", description="Show escalation metrics")
	async def escalation_stats(self, interaction: discord.Interaction) -> None:
		"""Return simple escalation metrics."""

		stats = await self.bot.escalation_service.stats()
		await interaction.response.send_message(f"Open escalations: {stats['open']}")


async def setup(bot: FieldAssistBot) -> None:
	"""Load cog into bot instance."""

	await bot.add_cog(AdminCog(bot))
