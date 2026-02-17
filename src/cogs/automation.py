"""Whitelisted remote automation commands."""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from src.bot import FieldAssistBot
from src.config import settings
from src.services.remote_automation_service import RemoteAutomationService
from src.utils.permissions import SRA_ROLE, has_any_role


class AutomationCog(commands.Cog):
	"""Run predefined automations from Discord safely."""

	def __init__(self, bot: FieldAssistBot) -> None:
		"""Initialize automation command handlers."""
		self.bot = bot

	@app_commands.command(name="run_job", description="Run a whitelisted remote automation job")
	@app_commands.describe(job_name="Allowed job name")
	@app_commands.choices(
		job_name=[
			app_commands.Choice(
				name="scto_dms_daily (download SurveyCTO CSV + run Stata DMS)",
				value=RemoteAutomationService.DAILY_DMS_JOB,
			)
		]
	)
	async def run_job(
		self,
		interaction: discord.Interaction,
		job_name: app_commands.Choice[str],
	) -> None:
		"""Execute a safe, pre-approved automation pipeline."""
		if settings.bot_admin_channel_id and (
			not interaction.channel_id
			or interaction.channel_id != settings.bot_admin_channel_id
		):
			await interaction.response.send_message(
				f"Use this command only in <#{settings.bot_admin_channel_id}>.",
				ephemeral=True,
			)
			return

		member = interaction.user if isinstance(interaction.user, discord.Member) else None
		if not has_any_role(member, {SRA_ROLE}):
			await interaction.response.send_message("insufficient permissions", ephemeral=True)
			return

		await interaction.response.defer()
		result = await self.bot.remote_automation_service.run_job(
			job_name=job_name.value,
			requester=str(interaction.user.id),
		)
		lines = (
			"\n".join(f"- {item}" for item in result.details)
			if result.details
			else "- no details"
		)
		await interaction.followup.send(f"{result.summary}\n{lines}")


async def setup(bot: FieldAssistBot) -> None:
	"""Load cog into bot instance."""
	await bot.add_cog(AutomationCog(bot))
