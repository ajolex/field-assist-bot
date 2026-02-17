"""Progress reporting command handlers."""

import discord
from discord import app_commands
from discord.ext import commands

from src.bot import FieldAssistBot
from src.utils.formatters import format_progress_text


class ProgressCog(commands.Cog):
	"""Progress and productivity slash commands."""

	def __init__(self, bot: FieldAssistBot) -> None:
		self.bot = bot

	@app_commands.command(name="progress", description="Show overall progress")
	async def progress(self, interaction: discord.Interaction) -> None:
		"""Return overall progress values."""

		await interaction.response.defer()
		values = await self.bot.progress_service.overall_progress()
		await interaction.followup.send(format_progress_text(values, "Overall progress"))

	@app_commands.command(name="team_status", description="Show team-specific progress")
	async def team_status(self, interaction: discord.Interaction, team_name: str) -> None:
		"""Return team metrics."""

		await interaction.response.defer()
		values = await self.bot.progress_service.team_status(team_name)
		await interaction.followup.send(format_progress_text(values, f"Team {team_name}"))

	@app_commands.command(name="fo_productivity", description="Show FO productivity")
	async def fo_productivity(self, interaction: discord.Interaction, fo_name: str) -> None:
		"""Return FO-level metrics."""

		await interaction.response.defer()
		values = await self.bot.progress_service.fo_productivity(fo_name)
		await interaction.followup.send(format_progress_text(values, f"FO {fo_name}"))


async def setup(bot: FieldAssistBot) -> None:
	"""Load cog into bot instance."""

	await bot.add_cog(ProgressCog(bot))
