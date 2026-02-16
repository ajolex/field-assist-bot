"""Assignment command handlers."""

import discord
from discord import app_commands
from discord.ext import commands

from src.bot import FieldAssistBot


class AssignmentsCog(commands.Cog):
	"""Assignment and location slash commands."""

	def __init__(self, bot: FieldAssistBot) -> None:
		self.bot = bot

	@app_commands.command(name="assignments", description="Show assignments for a team")
	async def assignments(self, interaction: discord.Interaction, team_name: str) -> None:
		"""Return assignments by team."""

		rows = await self.bot.assignment_service.team_assignments(team_name)
		if not rows:
			await interaction.response.send_message(f"No assignments for {team_name}.")
			return
		lines = [f"{row['case_id']} → {row['fo']}" for row in rows]
		await interaction.response.send_message("\n".join(lines))

	@app_commands.command(name="where_is", description="Find team for a case")
	async def where_is(self, interaction: discord.Interaction, case_id: str) -> None:
		"""Return assignment row for given case ID."""

		row = await self.bot.assignment_service.where_is_case(case_id)
		if row is None:
			await interaction.response.send_message("Case not found in assignments.")
			return
		await interaction.response.send_message(
			f"{case_id} is assigned to {row['team']} ({row['fo']})"
		)

	@app_commands.command(name="team_for", description="Find team for FO")
	async def team_for(self, interaction: discord.Interaction, fo_name: str) -> None:
		"""Return team for a field officer."""

		team = await self.bot.assignment_service.team_for_fo(fo_name)
		if team is None:
			await interaction.response.send_message("FO not found.")
			return
		await interaction.response.send_message(f"{fo_name} is assigned to {team}")


async def setup(bot: FieldAssistBot) -> None:
	"""Load cog into bot instance."""

	await bot.add_cog(AssignmentsCog(bot))
