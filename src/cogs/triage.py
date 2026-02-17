"""Field issue triage and ticketing commands."""

import discord
from discord import app_commands
from discord.ext import commands

from src.bot import FieldAssistBot
from src.utils.permissions import FC_ROLE, SRA_ROLE, has_any_role

STATUS_CHOICES = [
	app_commands.Choice(name="open", value="open"),
	app_commands.Choice(name="triaged", value="triaged"),
	app_commands.Choice(name="in_progress", value="in_progress"),
	app_commands.Choice(name="blocked", value="blocked"),
	app_commands.Choice(name="resolved", value="resolved"),
]


class TriageCog(commands.Cog):
	"""Commands for creating and managing structured field issues."""

	def __init__(self, bot: FieldAssistBot) -> None:
		"""Initialize triage command handlers."""
		self.bot = bot
		self.create_issue_menu = app_commands.ContextMenu(
			name="Create Field Issue",
			callback=self.create_issue_from_message,
		)
		try:
			self.bot.tree.add_command(self.create_issue_menu)
		except app_commands.CommandAlreadyRegistered:
			pass

	async def cog_unload(self) -> None:
		"""Unregister context menu on unload."""
		self.bot.tree.remove_command(self.create_issue_menu.name, type=self.create_issue_menu.type)

	async def create_issue_from_message(
		self,
		interaction: discord.Interaction,
		message: discord.Message,
	) -> None:
		"""Convert any message into a structured issue and spawn a thread."""
		await interaction.response.defer(ephemeral=True)
		description = message.content.strip() or "(no message text)"
		screenshot_urls = [
			attachment.url
			for attachment in message.attachments
			if (attachment.content_type or "").startswith("image/")
			or attachment.filename.lower().endswith(
				(".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif")
			)
		]
		issue = await self.bot.issue_triage_service.create_issue(
			reporter_id=str(interaction.user.id),
			source_channel_id=str(message.channel.id),
			source_message_id=str(message.id),
			description=description,
			screenshot_urls=screenshot_urls,
		)

		summary = self.bot.issue_triage_service.render_summary(issue)
		thread: discord.Thread | None = None
		summary_msg: discord.Message | None = None
		try:
			thread = await message.create_thread(name=f"{issue.issue_id} {issue.form_name}"[:95])
			summary_msg = await thread.send(summary)
			await summary_msg.pin(reason=f"Issue summary pin for {issue.issue_id}")
		except (discord.Forbidden, discord.HTTPException):
			try:
				summary_msg = await message.channel.send(summary)
			except (discord.Forbidden, discord.HTTPException):
				summary_msg = None

		if thread and summary_msg:
			await self.bot.issue_triage_service.attach_thread(
				issue_id=issue.issue_id,
				thread_channel_id=str(thread.id),
				summary_message_id=str(summary_msg.id),
			)

		destination = thread.mention if thread else "current channel"
		await interaction.followup.send(
			f"Created issue **{issue.issue_id}** with status **{issue.status}** in {destination}.",
			ephemeral=True,
		)

	@app_commands.command(
		name="issue_update",
		description="Update issue status/owner and append status log",
	)
	@app_commands.describe(
		issue_id="Issue ID like FI-20260217-...",
		status="New status",
		note="Short update note",
		owner="Optional owner override",
	)
	@app_commands.choices(status=STATUS_CHOICES)
	async def issue_update(
		self,
		interaction: discord.Interaction,
		issue_id: str,
		status: app_commands.Choice[str],
		note: str,
		owner: str | None = None,
	) -> None:
		"""Update issue status and keep lightweight status history."""
		member = interaction.user if isinstance(interaction.user, discord.Member) else None
		if not has_any_role(member, {SRA_ROLE, FC_ROLE}):
			await interaction.response.send_message("insufficient permissions", ephemeral=True)
			return

		await interaction.response.defer(ephemeral=True)
		updated = await self.bot.issue_triage_service.update_status(
			issue_id=issue_id.strip(),
			status=status.value,
			actor=str(interaction.user.id),
			note=note.strip(),
			owner=owner.strip() if owner else None,
		)
		if updated is None:
			await interaction.followup.send(f"Issue `{issue_id}` not found.", ephemeral=True)
			return

		await interaction.followup.send(
			f"Updated `{updated.issue_id}` -> status `{updated.status}`, owner `{updated.owner}`.",
			ephemeral=True,
		)

	@app_commands.command(name="issue_show", description="Show issue summary and latest status log")
	@app_commands.describe(issue_id="Issue ID")
	async def issue_show(self, interaction: discord.Interaction, issue_id: str) -> None:
		"""Display structured issue and recent updates."""
		await interaction.response.defer(ephemeral=True)
		issue = await self.bot.issue_triage_service.get_issue(issue_id.strip())
		if issue is None:
			await interaction.followup.send(f"Issue `{issue_id}` not found.", ephemeral=True)
			return

		history = await self.bot.issue_triage_service.get_status_history(issue.issue_id, limit=8)
		history_text = "\n".join(
			(
				f"- {row.get('timestamp', '')}: {row.get('status', '')} "
				f"by {row.get('actor', '')} — {row.get('note', '')}"
			)
			for row in history
		) or "- no updates yet"
		summary = self.bot.issue_triage_service.render_summary(issue)
		await interaction.followup.send(
			f"{summary}\n\n**Status Log**\n{history_text}",
			ephemeral=True,
		)


async def setup(bot: FieldAssistBot) -> None:
	"""Load cog into bot instance."""
	await bot.add_cog(TriageCog(bot))
