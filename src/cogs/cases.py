"""Case management command handlers."""

import discord
from discord import app_commands
from discord.ext import commands

from src.bot import FieldAssistBot
from src.utils.formatters import format_case_embed_text, format_escalation_text
from src.utils.permissions import FC_ROLE, SRA_ROLE, has_any_role


class CasesCog(commands.Cog):
	"""Case-related slash commands."""

	def __init__(self, bot: FieldAssistBot) -> None:
		self.bot = bot

	@app_commands.command(name="check_case", description="Check case details")
	async def check_case(self, interaction: discord.Interaction, case_id: str) -> None:
		"""Return redacted case details."""

		await interaction.response.defer()
		case = await self.bot.case_service.lookup_case(case_id)
		redacted = self.bot.case_service.redact_pii(case)
		await interaction.followup.send(format_case_embed_text(redacted))

	@app_commands.command(name="case_status", description="Get case status summary")
	async def case_status(self, interaction: discord.Interaction, case_id: str) -> None:
		"""Return quick status text."""

		await interaction.response.defer()
		status = await self.bot.case_service.case_status(case_id)
		await interaction.followup.send(status)

	@app_commands.command(name="team_cases", description="List open cases for a team")
	async def team_cases(self, interaction: discord.Interaction, team_name: str) -> None:
		"""List open cases for selected team."""

		await interaction.response.defer()
		cases = await self.bot.case_service.team_cases(team_name)
		if not cases:
			await interaction.followup.send(f"No open cases found for {team_name}.")
			return
		lines = [f"{case.case_id} ({case.barangay or 'unknown barangay'})" for case in cases]
		await interaction.followup.send("\n".join(lines))

	@app_commands.command(name="request_reopen", description="Request case reopening")
	async def request_reopen(
		self,
		interaction: discord.Interaction,
		case_id: str,
		reason: str,
	) -> None:
		"""Create reopen request with role checks."""

		member = interaction.user if isinstance(interaction.user, discord.Member) else None
		if not has_any_role(member, {SRA_ROLE, FC_ROLE}):
			await interaction.response.send_message("insufficient permissions", ephemeral=True)
			return
		await interaction.response.defer()
		await self.bot.case_service.request_reopen(case_id, interaction.user.name, reason)
		escalation_id = await self.bot.escalation_service.create_escalation(
			requester=interaction.user.name,
			reason=f"Reopen request for {case_id}: {reason}",
			channel=f"#{interaction.channel.name if interaction.channel else 'unknown'}",
			case_id=case_id,
		)
		await interaction.followup.send(format_escalation_text(escalation_id))


async def setup(bot: FieldAssistBot) -> None:
	"""Load cog into bot instance."""

	await bot.add_cog(CasesCog(bot))
