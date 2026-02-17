"""Announcement command handlers."""

import discord
from discord import app_commands
from discord.ext import commands

from src.bot import FieldAssistBot
from src.utils.permissions import SRA_ROLE, has_any_role


class AnnouncementsCog(commands.Cog):
	"""Manual announcement trigger commands."""

	def __init__(self, bot: FieldAssistBot) -> None:
		self.bot = bot

	@app_commands.command(name="announce", description="Send templated announcement")
	async def announce(
		self,
		interaction: discord.Interaction,
		template: str,
		value: str,
	) -> None:
		"""Render and send announcement from template."""

		member = interaction.user if isinstance(interaction.user, discord.Member) else None
		if not has_any_role(member, {SRA_ROLE}):
			await interaction.response.send_message("insufficient permissions", ephemeral=True)
			return
		await interaction.response.defer()
		key = "summary" if template == "evening_summary" else "target"
		if template == "form_update":
			content = self.bot.announcement_service.from_template(
				template,
				form="HH Survey",
				version=value,
			)
		else:
			content = self.bot.announcement_service.from_template(template, **{key: value})
		await self.bot.announcement_service.log_announcement(
			template,
			f"#{interaction.channel.name if interaction.channel else 'unknown'}",
			content,
		)
		await interaction.followup.send(content)

	@app_commands.command(name="morning_briefing", description="Manual morning briefing")
	async def morning_briefing(self, interaction: discord.Interaction) -> None:
		"""Send standard morning briefing announcement."""

		await interaction.response.defer()
		content = self.bot.announcement_service.from_template("morning_briefing", target="3.5/day")
		await self.bot.announcement_service.log_announcement(
			"morning_briefing",
			f"#{interaction.channel.name if interaction.channel else 'unknown'}",
			content,
		)
		await interaction.followup.send(content)


async def setup(bot: FieldAssistBot) -> None:
	"""Load cog into bot instance."""

	await bot.add_cog(AnnouncementsCog(bot))
