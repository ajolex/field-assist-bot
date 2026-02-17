"""Form version command handlers."""

import discord
from discord import app_commands
from discord.ext import commands

from src.bot import FieldAssistBot


class FormsCog(commands.Cog):
	"""Handles form version and changelog commands."""

	def __init__(self, bot: FieldAssistBot) -> None:
		self.bot = bot

	@app_commands.command(name="form_version", description="Get current form versions")
	async def form_version(self, interaction: discord.Interaction) -> None:
		"""Return form version map."""

		await interaction.response.defer()
		versions = await self.bot.survey_client.get_form_versions()
		lines = [f"{name}: {version}" for name, version in versions.items()]
		await interaction.followup.send("\n".join(lines) or "No form versions found.")

	@app_commands.command(name="form_changelog", description="Show latest form changes")
	async def form_changelog(self, interaction: discord.Interaction) -> None:
		"""Return a placeholder changelog summary."""

		await interaction.response.defer()
		versions = await self.bot.survey_client.get_form_versions()
		lines = [f"Updated: {name} → {version}" for name, version in versions.items()]
		await interaction.followup.send("\n".join(lines) or "No changelog entries.")


async def setup(bot: FieldAssistBot) -> None:
	"""Load cog into bot instance."""

	await bot.add_cog(FormsCog(bot))
